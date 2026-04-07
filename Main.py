from Script.UI import UI
from Script.Device import Hardware
from Script.Globals import *
from Script.Database.SQLite import Operator
from Script.Publisher import EventBroadcaster


class Application:
    def __init__(self):
        self.hw_cmd_queue = multiprocessing.Queue()  # main proc to sub proc
        self.hw_evt_queue = multiprocessing.Queue()  # sub proc to main proc
        self.ui_cmd_queue = queue.Queue()  # frontend to backend (both main proc)
        self.evt_bcst = EventBroadcaster()  # backend to frontend (both main proc)
        self.app_config = AppConfig()
        self.db_operator = Operator(self.evt_bcst, self.app_config)
        self.data_ft = Formatter()

        self.app_registry = AppRegistry()
        self.app_registry.register('evt', self.hw_evt_queue)
        self.app_registry.register('cmd', self.ui_cmd_queue)
        self.app_registry.register('evt_bcst', self.evt_bcst)
        self.app_registry.register('config', self.app_config)
        self.app_registry.register('db_op', self.db_operator)
        self.app_registry.register('data_ft', self.data_ft)

        self.hw_process = None
        self.App_UI = None
        self.page = None
        self.running = False

    def run(self):
        try:
            self.hw_process = Hardware.Service(self.hw_cmd_queue, self.hw_evt_queue)
            self.hw_process.start()
            flet.app(lambda page: self.init_app(page, self.app_config, self.data_ft, self.db_operator))
        except Exception as e:
            self.report_error(e)
        finally:
            self.cleanup()

    def init_app(self, page: flet.Page, config: AppConfig, data_ft: Formatter, db_op: Operator):
        self.page = page
        self.running = True

        self.App_UI = UI.Entity(page, config, data_ft, db_op)
        self.App_UI.init()
        self.App_UI.intro.start()

        threading.Thread(target=self.event_listener, daemon=True).start()
        threading.Thread(target=self.command_listener, daemon=True).start()

    def event_listener(self):
        while self.running:
            try:
                event, device = self.hw_evt_queue.get(timeout=0.1)
                self.evt_bcst.publish(USBEvent(type=event, device=device))
            except queue.Empty:
                continue
            except Exception as e:
                self.report_error(e)

    def command_listener(self):
        while self.running:
            try:
                cmd = self.ui_cmd_queue.get(timeout=0.1)
                self.hw_cmd_queue.put(cmd)
            except queue.Empty:
                continue
            except Exception as e:
                self.report_error(e)

    def cleanup(self):
        self.running = False
        time.sleep(0.2)
        if self.hw_process and self.hw_process.is_alive():
            self.command_hardware(type='stop')
            self.hw_process.join(timeout=3)

            if self.hw_process.is_alive():
                self.hw_process.terminate()
        self.evt_bcst.subscribers.clear()

    def command_hardware(self, type='', vid='', pid='', devices=None, payload='', mode=''):
        self.hw_cmd_queue.put({'type': f'{type}',
                               'vid': f'{vid}',
                               'pid': f'{pid}',
                               'devices': devices,
                               'payload': f'{payload}',
                               'mode': f'{mode}'
                               })

    def report_error(self, error):
        self.hw_evt_queue.put((
            'error', {
                'physical_id': None,
                'vendor_id': None,
                'product_id': None,
                'info': f'Error: {error}',
                'report': {
                    'timestamp': self.evt_bcst.get_timestamp(),
                    'event': 'Error',
                    'detail': f'{error}'
                }
            }))


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = Application()
    app.run()
