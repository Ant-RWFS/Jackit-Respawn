class HID(object):
    def __init__(self, address, payload):
        self.address = address
        self.payload = list(payload) if payload else [0] * 15
        self.device_vendor = 'Dell'

    def key(self, payload, key):
        new_payload = list(payload)
        new_payload[0] ^= key['mod']
        new_payload[2] ^= key['hid']
        return new_payload

    def frame(self, key=None):
        if key is None:
            key = {'hid': 0, 'mod': 0}
        return self.key(self.payload, key)

    def build_frames(self, attack):
        for i in range(len(attack)):
            key = attack[i]
            key['frames'] = []
            if key.get('hid') or key.get('mod'):
                key['frames'].append([self.frame(key), 10])
                key['frames'].append([self.payload, 10])
            elif key['sleep']:
                count = int(key['sleep']) / 10
                for i in range(0, int(count)):
                    key['frames'].append([self.frame(), 10])

    @classmethod
    def fingerprint(cls, p):
        if len(p) == 15:
            return cls
        return None

    @classmethod
    def description(cls):
        return 'Dell HID'
