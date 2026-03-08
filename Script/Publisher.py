import threading
from datetime import datetime
import flet as ft
from Script.Data import *


class File:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, page: ft.Page, config):
        self.page = page
        self.config = config
        self.file_save_picker = ft.FilePicker()
        self.file_open_picker = ft.FilePicker()
        self.init()

    def init(self):
        self.page.overlay.extend([self.file_save_picker, self.file_open_picker])

    def open_file(self, e, extensions: list, content_widget):
        self.file_open_picker.on_result = lambda event: self.read_file(event, content_widget)
        self.file_open_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=extensions
        )

    def save_file(self, e, name: str, extensions: list, content_widget):
        self.file_save_picker.on_result = lambda event: self.write_file(event, content_widget)
        self.file_save_picker.save_file(
            file_name=name,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=extensions
        )

    def read_file(self, e: ft.FilePickerResultEvent, text: ft.TextField):
        if e.files and len(e.files) > 0:
            file = e.files[0]
            try:
                with open(file.path, 'r', encoding='utf-8') as f:
                    text.value = f.read()
            except Exception as ex:
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text(
                            value=f"Failed to read file: {ex}",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        duration=2000,
                        bgcolor=self.config.FIXED_COLORS['warning'],
                    )
                )
            self.page.update()

    def write_file(self, e: ft.FilePickerResultEvent, content_widget):
        if e.path:
            try:
                content = content_widget.value if isinstance(content_widget, ft.TextField) else str(content_widget)
                with open(e.path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text(value=f"File saved to: {e.path}",
                                        text_align=ft.TextAlign.CENTER, ),
                        duration=2000,
                    )
                )
            except Exception as ex:
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text(value=f"Failed to save file: {ex}"),
                        duration=2000,
                        bgcolor=self.config.FIXED_COLORS['warning'],
                    )
                )
            self.page.update()


class EventBroadcaster:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.subscribers = {}
        self.lock = threading.Lock()

    def subscribe(self, callback, event_type='all'):
        with self.lock:
            if isinstance(event_type, str):
                event_types = [event_type]
            else:
                event_types = event_type

            for et in event_types:
                if et not in self.subscribers:
                    self.subscribers[et] = []
                self.subscribers[et].append(callback)

    def unsubscribe(self, event_type, callback):
        with self.lock:
            if isinstance(event_type, str):
                event_types = [event_type]
            else:
                event_types = event_type

            for et in event_types:
                if et in self.subscribers:
                    self.subscribers[et] = [
                        cb for cb in self.subscribers[et]
                        if cb != callback
                    ]

    def publish(self, event: USBEvent):
        threading.Thread(
            target=self.notify_subscribers,
            args=(event,),
            daemon=True
        ).start()

    def notify_subscribers(self, event: USBEvent):
        with self.lock:
            callbacks = self.subscribers.get(event.type, []).copy()
            callbacks.extend(self.subscribers.get('all', []))

        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                import traceback
                print(f"Error in callback {callback.__name__}: {e}")
                print(f"Event data: {event.__dict__ if hasattr(event, '__dict__') else event}")
                traceback.print_exc()

    def get_timestamp(self):
        return datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')