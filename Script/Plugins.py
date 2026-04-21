class DriverRegistry:
    instance = None
    drivers = {}
    vid_pid_set = set()

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    @classmethod
    def discover_drivers(cls):
        try:
            import Plugin.Device
            for name in Plugin.Device.__all__:
                driver_class = getattr(Plugin.Device, name)
                if hasattr(driver_class, 'ID'):
                    cls.drivers[driver_class.ID] = driver_class
        except ImportError as e:
            print(f"Warning: Could not load Device plugins: {e}")
        return cls.drivers

    @classmethod
    def discover_vid_pid_set(cls):
        try:
            import Plugin.Device
            for name in Plugin.Device.__all__:
                driver_class = getattr(Plugin.Device, name)
                if hasattr(driver_class, 'VENDOR_ID') and hasattr(driver_class, 'PRODUCT_ID'):
                    cls.vid_pid_set.add(
                        (f'{driver_class.VENDOR_ID:04X}'.lower(), f'{driver_class.PRODUCT_ID:04X}'.lower()))
        except ImportError as e:
            print(f"Warning: Could not load Device plugins for VID/PID: {e}")

        if len(cls.vid_pid_set) > 0:
            return cls.vid_pid_set
        else:
            return None


class FingerprintRegistry:
    instance = None
    fingerprints = {}

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    @classmethod
    def discover(cls):
        try:
            import Plugin.HID
            for name in Plugin.HID.__all__:
                hid_class = getattr(Plugin.HID, name)
                cls.fingerprints[name] = hid_class
        except ImportError as e:
            print(f"Warning: Could not load HID plugins: {e}")
        return cls.fingerprints
