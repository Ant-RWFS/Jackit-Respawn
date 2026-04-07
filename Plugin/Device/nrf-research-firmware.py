import usb

try:
    from fcntl import ioctl
except ImportError:
    ioctl = lambda *args: None

USB_TIMEOUT = 2500
USB_RESET = ord('U') << (4 * 2) | 20

RF_RATE = {
    "250K": 0,
    "1M": 1,
    "2M": 2
}

NRF24_COMMANDS = {
    "TRANSMIT_PAYLOAD": 0x04,
    "SNIFFER_MODE": 0x05,
    "PROMISCUOUS_MODE": 0x06,
    "TONE_TEST_MODE": 0x07,
    "TRANSMIT_ACK_PAYLOAD": 0x08,
    "SET_CHANNEL": 0x09,
    "GET_CHANNEL": 0x0A,
    "ENABLE_LNA_PA": 0x0B,
    "TRANSMIT_PAYLOAD_GENERIC": 0x0C,
    "PROMISCUOUS_MODE_GENERIC": 0x0D,
    "RECEIVE_PAYLOAD": 0x12
}


class Driver(object):
    VENDOR_ID = 0x1915
    PRODUCT_ID = 0x0102
    ID = f'{VENDOR_ID:04X}_{PRODUCT_ID:04X}'  # ID String: '1915_0102', which is used for registry

    def __init__(self, index=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = None
        self.vendor_id = self.VENDOR_ID
        self.product_id = self.PRODUCT_ID
        self.init_device(index)

    def init_device(self, index=0):
        try:
            self.device = list(usb.core.find(find_all=True, idVendor=self.vendor_id, idProduct=self.product_id))[index]
            self.device.set_configuration()
        except usb.core.USBError as ex:
            return ex
        except Exception as ex:
            return ex

    def execute_command(self, command, data):
        data = [command] + list(data)
        self.device.write(0x01, data, timeout=USB_TIMEOUT)

    def activate_promiscuous_mode(self, prefix=[]):
        self.execute_command(NRF24_COMMANDS["PROMISCUOUS_MODE"], [len(prefix)] + prefix)
        self.device.read(0x81, 64, timeout=USB_TIMEOUT)

    def activate_promiscuous_mode_generic(self, prefix=[], rate=RF_RATE["2M"]):
        self.execute_command(NRF24_COMMANDS["PROMISCUOUS_MODE_GENERIC"], [len(prefix), rate] + prefix)
        self.device.read(0x81, 64, timeout=USB_TIMEOUT)

    def activate_sniffer_mode(self, address):
        self.execute_command(NRF24_COMMANDS["SNIFFER_MODE"], [len(address)] + address)
        self.device.read(0x81, 64, timeout=USB_TIMEOUT)

    def activate_tone_test_mode(self):
        self.execute_command(NRF24_COMMANDS["TONE_TEST_MODE"], [])
        self.device.read(0x81, 64, timeout=USB_TIMEOUT)

    def recv_payload(self):
        self.execute_command(NRF24_COMMANDS["RECEIVE_PAYLOAD"], ())
        return self.device.read(0x81, 64, timeout=USB_TIMEOUT)

    def send_payload(self, payload, timeout=4, retransmits=15):
        data = [len(payload), timeout, retransmits] + payload
        self.execute_command(NRF24_COMMANDS["TRANSMIT_PAYLOAD"], data)
        return self.device.read(0x81, 64, timeout=USB_TIMEOUT)[0] > 0

    def send_ack_payload(self, payload):
        data = [len(payload)] + payload
        self.execute_command(NRF24_COMMANDS["TRANSMIT_ACK_PAYLOAD"], data)
        return self.device.read(0x81, 64, timeout=USB_TIMEOUT)[0] > 0

    def send_payload_generic(self, payload, address=[0x33, 0x33, 0x33, 0x33, 0x33]):
        data = [len(payload), len(address)] + payload + address
        self.execute_command(NRF24_COMMANDS["TRANSMIT_PAYLOAD_GENERIC"], data)
        return self.device.read(0x81, 64, timeout=USB_TIMEOUT)[0] > 0

    def get_channel(self):
        self.execute_command(NRF24_COMMANDS["GET_CHANNEL"], [])
        return self.device.read(0x81, 64, timeout=USB_TIMEOUT)

    def set_channel(self, channel):
        if channel in range(0, 126):
            self.execute_command(NRF24_COMMANDS["SET_CHANNEL"], [channel])
            self.device.read(0x81, 64, timeout=USB_TIMEOUT)
        else:
            raise ValueError("Channel Out Of Range 0-125")

    def activate_LNA(self):
        self.execute_command(NRF24_COMMANDS["ENABLE_LNA_PA"], [])
        self.device.read(0x81, 64, timeout=USB_TIMEOUT)
