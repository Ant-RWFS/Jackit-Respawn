import flet
import queue
import Plugin.HID
import Plugin.Device
import multiprocessing
from typing import Dict, Any
from Script.Publisher import *
from Script.Database.SQLite import Operator
from Script.Config.Settings import AppConfig
from Script.Data import Formatter


class AppRegistry:
    instance = None
    registry: Dict[str, Any] = {}

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    @classmethod
    def register(cls, name: str, obj: Any) -> None:
        cls.registry[name] = obj

    @classmethod
    def get(cls, name: str) -> Any:
        return cls.registry.get(name)

    @classmethod
    def clear(cls) -> None:
        cls.registry.clear()


def page() -> 'flet.Page':
    return AppRegistry.get('page')


def config() -> 'AppConfig':
    return AppRegistry.get('config')


def evt() -> 'multiprocessing.Queue':
    return AppRegistry.get('evt')


def cmd() -> 'queue.Queue':
    return AppRegistry.get('cmd')


def file_op() -> 'File':
    return AppRegistry.get('file_op')


def evt_bcst() -> 'EventBroadcaster':
    return AppRegistry.get('evt_bcst')


def db_op() -> 'Operator':
    return AppRegistry.get('db_op')


def data_ft() -> 'Formatter':
    return AppRegistry.get('data_ft')


class FingerprintRegistry:
    fingerprints = {}

    @classmethod
    def discover(cls):
        for name in Plugin.HID.__all__:
            hid_class = getattr(Plugin.HID, name)
            cls.fingerprints[name] = hid_class
        return cls.fingerprints


class DriverRegistry:
    drivers = {}
    vid_pid_set = set()

    @classmethod
    def discover_drivers(cls):
        for name in Plugin.Device.__all__:
            driver_class = getattr(Plugin.Device, name)
            if hasattr(driver_class, 'ID'):
                cls.drivers[driver_class.ID] = driver_class
        return cls.drivers

    @classmethod
    def discover_vid_pid_set(cls):
        for name in Plugin.Device.__all__:
            driver_class = getattr(Plugin.Device, name)
            if hasattr(driver_class, 'VENDOR_ID') and hasattr(driver_class, 'PRODUCT_ID'):
                cls.vid_pid_set.add((f'{driver_class.VENDOR_ID:04X}'.lower(), f'{driver_class.PRODUCT_ID:04X}'.lower()))
        if len(cls.vid_pid_set) > 0:
            return cls.vid_pid_set
        else:
            return None
