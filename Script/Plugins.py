import sys
import importlib


def reload_plugin_package(package_name: str):
    importlib.invalidate_caches()

    modules_to_remove = [
        name for name in list(sys.modules.keys())
        if name == package_name or name.startswith(f"{package_name}.")
    ]

    for name in modules_to_remove:
        sys.modules.pop(name, None)

    module = importlib.import_module(package_name)
    return importlib.reload(module)


class DriverRegistry:
    drivers = {}
    vid_pid_set = set()
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    @staticmethod
    def load_device_package():
        return reload_plugin_package("Plugin.Device")

    @classmethod
    def discover_drivers(cls):
        cls.drivers.clear()
        try:
            plugin_device = cls.load_device_package()
            for name in plugin_device.__all__:
                driver_class = getattr(plugin_device, name, None)
                if driver_class is not None and hasattr(driver_class, "ID"):
                    cls.drivers[driver_class.ID] = driver_class
        except ImportError as e:
            print(f"Warning: Could not load Device plugins: {e}")
        return cls.drivers

    @classmethod
    def discover_vid_pid_set(cls):
        cls.vid_pid_set.clear()
        try:
            plugin_device = cls.load_device_package()
            for name in plugin_device.__all__:
                driver_class = getattr(plugin_device, name, None)
                if (
                        driver_class is not None
                        and hasattr(driver_class, "VENDOR_ID")
                        and hasattr(driver_class, "PRODUCT_ID")
                ):
                    cls.vid_pid_set.add(
                        (
                            f"{driver_class.VENDOR_ID:04X}".lower(),
                            f"{driver_class.PRODUCT_ID:04X}".lower(),
                        )
                    )
        except ImportError as e:
            print(f"Warning: Could not load Device plugins for VID/PID: {e}")
        return cls.vid_pid_set


class FingerprintRegistry:
    fingerprints = {}

    @staticmethod
    def load_hid_package():
        return reload_plugin_package("Plugin.HID")

    @classmethod
    def discover(cls):
        cls.fingerprints.clear()
        try:
            plugin_hid = cls.load_hid_package()
            for name in plugin_hid.__all__:
                hid_class = getattr(plugin_hid, name, None)
                if hid_class is not None:
                    cls.fingerprints[name] = hid_class
        except ImportError as e:
            print(f"Warning: Could not load HID plugins: {e}")
        return cls.fingerprints

    @classmethod
    def get_name(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            return value if value in cls.fingerprints else None

        target_module = getattr(value, "__module__", None)
        target_name = getattr(value, "__name__", None)

        for name, hid_class in cls.fingerprints.items():
            if (
                    getattr(hid_class, "__module__", None) == target_module
                    and getattr(hid_class, "__name__", None) == target_name
            ):
                return name

        return None

    @classmethod
    def get_class(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            return cls.fingerprints.get(value)

        target_module = getattr(value, "__module__", None)
        target_name = getattr(value, "__name__", None)

        for hid_class in cls.fingerprints.values():
            if (
                    getattr(hid_class, "__module__", None) == target_module
                    and getattr(hid_class, "__name__", None) == target_name
            ):
                return hid_class

        return None
