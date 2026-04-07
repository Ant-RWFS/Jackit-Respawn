import queue
import threading
import multiprocessing as mp
from typing import Dict, Any
from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_MODEL_ID, ID_VENDOR_ID

from Script.Data import Formatter
from Script.Device.Operator.USB import *
from Script.Device.Operator.Payload import *


class Service(mp.Process):
    def __init__(self, cmd_queue: mp.Queue, evt_queue: mp.Queue):
        super().__init__()
        self.cmd_queue = cmd_queue
        self.evt_queue = evt_queue
        self.vid_pid_set = DriverRegistry.discover_vid_pid_set()
        self.daemon = True
        self.monitor = None
        self.data_ft = Formatter()
        self.processed_devices = set()
        self.action_threads = {}

    @staticmethod
    def is_parent_usb_device(device_id: str):
        device_id_upper = device_id.upper()
        if '&MI_' in device_id_upper:
            return False
        return True

    def run(self):
        self.monitor = USBMonitor()
        existing_devices = self.monitor.get_available_devices()
        for device_id, device_info in existing_devices.items():
            self.on_device_connected(device_id, device_info)

        self.monitor.start_monitoring(
            on_connect=self.on_device_connected,
            on_disconnect=self.on_device_disconnected
        )
        self.cmd_proc_loop()
        if self.monitor:
            self.monitor.stop_monitoring()

    def cmd_proc_loop(self):
        latest_id = None
        try:
            while True:
                try:
                    cmd = self.cmd_queue.get(timeout=0.1)
                    cmd_type, vid, pid = cmd['type'], cmd['vid'], cmd['pid']
                    physical_id = f"{cmd['vid']}_{cmd['pid']}".lower()
                    if self.is_device_online(physical_id):
                        if cmd_type == 'scan_start':
                            self.stop_action(physical_id)
                            self.start_scan(vid, pid, physical_id)
                            latest_id = physical_id
                        elif cmd_type == 'attack_start':
                            self.stop_action(physical_id)
                            payload = cmd['payload']
                            mode = cmd['mode']
                            targets = cmd['devices']
                            parse = cmd['parse']
                            language = cmd['language']
                            self.start_attack(vid, pid, physical_id, payload, mode, parse, targets, language)
                            latest_id = physical_id
                        elif cmd_type == 'scan_stop' or cmd_type == 'attack_stop':
                            self.stop_action(physical_id)
                        elif cmd_type == 'reload_device':
                            if latest_id:
                                self.stop_action(latest_id)
                            self.reload_device()
                    else:
                        self.device_event('offline', cmd['vid'], cmd['pid'])
                except queue.Empty:
                    continue
                except Exception as e:
                    self.error_report('Command Error', e)
        except Exception as e:
            self.error_report('Error', e)

    def reload_device(self):
        self.vid_pid_set = DriverRegistry.discover_vid_pid_set()

    def on_device_connected(self, device_id: str, device_info: Dict[str, Any]):
        vid = device_info.get(ID_VENDOR_ID, '').lower()
        pid = device_info.get(ID_MODEL_ID, '').lower()
        physical_id = f"{vid}_{pid}"

        if self.is_parent_usb_device(device_id) and (
                (vid, pid) in self.vid_pid_set) and (
                physical_id not in self.processed_devices):
            self.processed_devices.add(physical_id)

            self.device_event('add', vid, pid)

    def on_device_disconnected(self, device_id: str, device_info: Dict[str, Any]):
        vid = device_info.get(ID_VENDOR_ID, '').lower()
        pid = device_info.get(ID_MODEL_ID, '').lower()
        physical_id = f"{vid}_{pid}"

        if self.is_parent_usb_device(device_id) and (vid, pid) in self.vid_pid_set:
            self.processed_devices.discard(physical_id)
            self.device_event('remove', vid, pid)

    def is_device_online(self, physical_id: str):
        return physical_id.lower() in (self.processed_devices or set())

    def device_event(self, evt, vid, pid, info=None):
        self.evt_queue.put(
            (
                evt,
                {
                    'vendor_id': vid.upper() if vid else None,
                    'product_id': pid.upper() if pid else None,
                    'info': info if info else {},
                }
            )
        )

    def start_scan(self, vid, pid, physical_id):
        if physical_id in self.action_threads:
            return

        stop_event = threading.Event()
        t = threading.Thread(
            target=self.scan,
            args=(vid, pid, physical_id, stop_event),
            daemon=True
        )
        self.action_threads[physical_id] = {
            'thread': t,
            'event': stop_event,
            'running': True
        }
        t.start()

    def stop_action(self, physical_id):
        if physical_id not in self.action_threads:
            return

        info = self.action_threads[physical_id]
        if info['event']:
            info['event'].set()
        if info['thread'].is_alive():
            info['thread'].join(timeout=2.0)

        info['running'] = False
        del self.action_threads[physical_id]

    def start_attack(self, vid, pid, physical_id, payload, mode, parse, devices, language):
        if physical_id in self.action_threads or not devices:
            self.action_report(
                'atk_fin', physical_id, vid, pid, {}, {
                    'timestamp': self.data_ft.form_timestamp_str_in_year(),
                    'action': 'Rejected Action',
                    'payload': '',
                    'target_address': '',
                    'target_channels': '',
                    'target_hid': ''
                })
            return

        valid_hid_classes = set(FingerprintRegistry.discover().values())
        valid_devices = {}
        for addr, device_info in devices.items():
            device_class = device_info['device']
            if device_class in valid_hid_classes:
                valid_devices[addr] = device_info
        if not valid_devices and mode != 'Replay':
            self.action_report('atk_fin', physical_id, vid, pid, {}, {
                'timestamp': self.data_ft.form_timestamp_str_in_year(),
                'action': 'Invalid Device Action',
                'payload': '',
                'target_address': '',
                'target_channels': '',
                'target_hid': ''
            })
            return

        func, args, t, stop_event = None, (), None, None

        if mode == 'Mousejack':
            if parse:
                func = self.mousejack_attack
                args = (vid, pid, physical_id, devices, payload, language,)
            else:
                func = self.rawdata_attack
                args = (vid, pid, physical_id, devices, payload,)
        elif mode == 'Replay':
            if parse:
                func = self.replay_attack
                args = (vid, pid, physical_id, devices,)
            else:
                func = self.replay_rawdata
                args = (vid, pid, physical_id, devices, payload,)
        if func:
            stop_event = threading.Event()
            t = threading.Thread(
                target=func,
                args=args + (stop_event,),
                daemon=True
            )
            t.start()
            self.action_threads[physical_id] = {
                'thread': t,
                'event': stop_event,
                'running': True
            }

    def scan(self, vid, pid, physical_id, stop_event):
        scanner = Predator(vid, pid)
        device_count = 0
        last_data = {}
        try:
            while not stop_event.is_set():
                scanner.scan()
                if stop_event.is_set():
                    break
                if scanner.devices:
                    if device_count >= len(scanner.devices):
                        device_count = 0

                    addr = list(scanner.devices.keys())[device_count]
                    current_info = scanner.devices[addr]
                    is_new_data = False

                    if addr not in last_data:
                        is_new_data = True
                    else:
                        last = last_data[addr]
                        if (last.get('count') != current_info.get('count') or
                                last.get('payload') != current_info.get('payload') or
                                last.get('timestamp') != current_info.get('timestamp')):
                            is_new_data = True

                    if is_new_data:
                        last_data[addr] = {
                            'count': current_info.get('count'),
                            'payload': current_info.get('payload') if current_info.get('payload') else [],
                            'timestamp': current_info.get('timestamp'),
                            'channels': current_info.get('channels', []),
                        }
                        report = current_info.copy()
                        report['detector'] = f"VID:{vid} PID:{pid}"
                        self.action_report('recv', physical_id,
                                           vid, pid,
                                           current_info.copy(),
                                           report
                                           )

                    scanner.sniff(0.1, addr)
                    if device_count + 1 < len(scanner.devices):
                        device_count += 1
                    else:
                        device_count = 0
                else:
                    device_count = 0
        except Exception as e:
            self.error_report('Scan Failed', e)
        finally:
            self.action_report('scan_fin', physical_id, vid, pid, {}, {
                'timestamp': self.data_ft.form_timestamp_str_in_year(),
                'action': 'Scan Finish',
                'payload': '',
                'target_address': '',
                'target_channels': '',
                'target_hid': '',
            })
            scanner.close()

    def mousejack_attack(self, vid, pid, physical_id, targets, mal_cmd, language, stop_event):
        attacker = Predator(vid, pid)
        try:
            mal_code = DuckyParser(mal_cmd, language).parse()
            attacker.mousejack(targets, mal_code)
        except Exception as e:
            self.error_report('Mousejack Attack Failed', e)
        finally:
            self.action_report('atk_fin', physical_id, vid, pid, {}, {
                'timestamp': self.data_ft.form_timestamp_str_in_year(),
                'action': 'Mousejack',
                'payload': f'{mal_cmd}',
                'target_address': attacker.report_address(targets),
                'target_channels': attacker.report_channels(targets),
                'target_hid': attacker.report_hid(targets)
            })
            attacker.close()

    def rawdata_attack(self, vid, pid, physical_id, targets, payload, stop_event):
        attacker = Predator(vid, pid)
        try:
            attacker.attack_with_rawdata(targets, payload)
        except Exception as e:
            self.error_report('Rawdata Attack Failed', e)
        finally:
            self.action_report('atk_fin', physical_id, vid, pid, {}, {
                'timestamp': self.data_ft.form_timestamp_str_in_year(),
                'action': 'Rawdata',
                'payload': f'{payload}',
                'target_address': attacker.report_address(targets),
                'target_channels': attacker.report_channels(targets),
                'target_hid': attacker.report_hid(targets)
            })
            attacker.close()

    def replay_attack(self, vid, pid, physical_id, targets, stop_event):
        attacker = Predator(vid, pid)
        try:
            while not stop_event.is_set():
                attacker.replay(targets)
                time.sleep(0.01)
        except Exception as e:
            self.error_report('Replay Attack Failed', e)
        finally:
            self.action_report('atk_fin', physical_id, vid, pid, {}, {
                'timestamp': self.data_ft.form_timestamp_str_in_year(),
                'action': 'Replay',
                'payload': attacker.get_payload(targets),
                'target_address': attacker.report_address(targets),
                'target_channels': attacker.report_channels(targets),
                'target_hid': ''
            })
            attacker.close()

    def replay_rawdata(self, vid, pid, physical_id, targets, payload, stop_event):
        attacker = Predator(vid, pid)
        try:
            while not stop_event.is_set():
                attacker.attack_with_rawdata(targets, payload)
                time.sleep(0.01)
        except Exception as e:
            self.error_report('Replay Attack Failed', e)
        finally:
            self.action_report('atk_fin', physical_id, vid, pid, {}, {
                'timestamp': self.data_ft.form_timestamp_str_in_year(),
                'action': 'Replay',
                'payload': f'{payload}',
                'target_address': attacker.report_address(targets),
                'target_channels': attacker.report_channels(targets),
                'target_hid': ''
            })
            attacker.close()

    def action_report(self, action, physical_id, vid, pid, info, report):
        self.evt_queue.put((action, {
            'physical_id': physical_id,
            'vendor_id': vid,
            'product_id': pid,
            'info': info,
            'report': report
        }))

    def error_report(self, title, error):
        self.evt_queue.put((
            'error', {
                'physical_id': None,
                'vendor_id': None,
                'product_id': None,
                'info': f'{title}: {error}',
                'report': {
                    'timestamp': self.data_ft.form_timestamp_str_in_year(),
                    'event': f'{title}',
                    'detail': f'{error}'
                }
            }))
