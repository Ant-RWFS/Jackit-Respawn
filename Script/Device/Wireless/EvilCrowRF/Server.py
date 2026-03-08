import socket
import threading
import sys
import signal
import select
from typing import Optional


class EvilCrowRFServer:
    def __init__(self, port: int = 4444):
        self.buffer_size = 4096
        self.running = True
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.client_address: Optional[tuple] = None
        self.port = port

    def signal_handler(self, sig, frame):
        """优雅处理Ctrl+C"""
        print("\n[*] Shutting down server...")
        self.running = False
        self._cleanup()
        sys.exit(0)

    def _cleanup(self):
        """统一清理资源"""
        print("[*] Cleaning up resources...")
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.client_socket.close()
            self.client_socket = None

        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None

    def handle_client(self):
        """接收客户端数据（守护线程）"""
        while self.running and self.client_socket:
            try:
                # 使用select避免阻塞
                ready, _, _ = select.select([self.client_socket], [], [], 1.0)
                if not ready:
                    continue

                data = self.client_socket.recv(self.buffer_size)
                if not data:
                    print("\n[!] Client disconnected.")
                    self.running = False
                    break

                print(data.decode('utf-8', errors='replace'), end='', flush=True)
            except Exception as e:
                if self.running:
                    print(f"\n[!] Error receiving data: {e}")
                    self.running = False
                break

    def send_commands(self):
        """发送用户输入到客户端（守护线程）"""
        while self.running and self.client_socket:
            try:
                # 使用select处理input的超时
                if select.select([sys.stdin], [], [], 1.0)[0]:
                    command = input()
                else:
                    continue

                if command.lower() in ['exit', 'quit']:
                    print("[*] Exiting...")
                    self.running = False
                    break

                command += '\n'
                self.client_socket.sendall(command.encode('utf-8'))
            except EOFError:
                print("\n[!] Input stream closed.")
                self.running = False
                break
            except Exception as e:
                if self.running:
                    print(f"\n[!] Error sending command: {e}")
                    self.running = False
                break

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        # 命令行参数解析
        if '--port' in sys.argv:
            try:
                port_index = sys.argv.index('--port') + 1
                if port_index < len(sys.argv):
                    self.port = int(sys.argv[port_index])
            except (ValueError, IndexError):
                print("[!] Invalid port number. Using default.")

        print(f"[*] Server started on port {self.port}")

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(1.0)  # 允许定期检查running标志
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(1)

            print(f"[*] Server listening on port {self.port}")

            # 循环接受连接，支持running标志
            while self.running:
                try:
                    self.client_socket, self.client_address = self.server_socket.accept()
                    break
                except socket.timeout:
                    continue

            if not self.running:
                return

            print(f"[*] Connection established with {self.client_address[0]}:{self.client_address[1]}")

            # 启动线程（非daemon，确保完成当前操作）
            recv_thread = threading.Thread(target=self.handle_client)
            send_thread = threading.Thread(target=self.send_commands)

            recv_thread.start()
            send_thread.start()

            recv_thread.join()
            send_thread.join()

        except KeyboardInterrupt:
            print("\n[*] Server interrupted by user.")
        except Exception as e:
            print(f"[!] Server error: {e}")
        finally:
            self._cleanup()
            print("[*] Server shut down.")
