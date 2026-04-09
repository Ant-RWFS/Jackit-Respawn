import threading
from Script.Data import *
from datetime import datetime


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
