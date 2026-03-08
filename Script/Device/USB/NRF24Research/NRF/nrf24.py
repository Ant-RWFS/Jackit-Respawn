import usb

try:
    from fcntl import ioctl
except ImportError:
    ioctl = lambda *args: None

USB_TIMEOUT = 2500
USB_RESET = ord('U') << (4 * 2) | 20

ID = {
    "VENDOR_ID": 0x1915,
    "PRODUCT_ID": 0x0102
}

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


class NRF24:
    def __init__(self, index=0):
        self.device = None
        self.vendor_id = ID["VENDOR_ID"]
        self.product_id = ID["PRODUCT_ID"]
        self.init_device(index)

    def init_device(self, index=0):
        try:
            self.device = list(usb.core.find(find_all=True, idVendor=self.vendor_id, idProduct=self.product_id))[index]
            self.device.set_configuration()
        except usb.core.USBError as ex:
            return ex
        except Exception as ex:
            return ex

    def reset_on_linux(self):
        device = self.device
        bus = str(device.bus).zfill(3)
        addr = str(device.address).zfill(3)
        filename = "/dev/bus/usb/%s/%s" % (bus, addr)
        try:
            ioctl(open(filename, "w"), USB_RESET, 0)
        except IOError:
            print("Unable to reset device %s" % filename)

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

    def recv_payload(self):  #FIFO DATA
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
        if channel in range(0, 126):  #channel from 0 to 125
            self.execute_command(NRF24_COMMANDS["SET_CHANNEL"], [channel])
            self.device.read(0x81, 64, timeout=USB_TIMEOUT)
        else:
            raise ValueError("Channel Out Of Range 0-125")

    def avctivate_LNA(self):
        self.execute_command(NRF24_COMMANDS["ENABLE_LNA_PA"], [])
        self.device.read(0x81, 64, timeout=USB_TIMEOUT)

# if __name__ == '__main__':
#     nrf=NRF24()
#     print(nrf.device)

# """
#     Copyright (C) 2016 Bastille Networks
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
# """
# import usb
# from usb import core as _usb_core  # NOQA
# import usb.core
# import usb.util
# # from fcntl import ioctl
#
# # USB commands
# USB_COMMANDS = {
#     'transmit_payload': 0x04,
#     'sniffer_mode': 0x05,
#     'promiscuous_mode': 0x06,
#     'tone_test_mode': 0x07,
#     'transmit_ack_payload': 0x08,
#     'set_channel': 0x09,
#     'get_channel': 0x0A,
#     'enable_lan_pa': 0x0B,
#     'transmit_payload_generic': 0x0C,
#     'promiscuous_mode_generic': 0x0D,
#     'receive_payload': 0x12,
# }
# # nRF24LU1+ registers
# RF_CH = 0x05
#
# # RF data rates
# RF_DATA_RATE = {
#     '250k': 0,
#     '1m': 1,
#     '2m': 2,
# }
#
#
# # nRF24LU1+ radio dongle
# class NRF24:
#     # Sufficiently long timeout for use in a VM
#     usb_timeout = 2500
#
#     # Constructor
#     def __init__(self, index=0):
#         self.dongle = list(usb.core.find(idVendor=0x1915, idProduct=0x0102, find_all=True))[index]
#         self.dongle.set_configuration()
#
#     # Put the radio in pseudo-promiscuous mode
#     def enter_promiscuous_mode(self, prefix):
#         self.send_usb_command(USB_COMMANDS['promiscuous_mode'], [len(prefix)] + prefix)
#         self.dongle.read(0x81, 64, timeout=NRF24.usb_timeout)
#         # if len(prefix) > 0: logging.debug('Entered promiscuous mode with address prefix {0}'.format(':'.join('{
#         # :02X}'.format(b) for b in prefix))) else: logging.debug('Entered promiscuous mode')
#
#     # Put the radio in pseudo-promiscuous mode without CRC checking
#     def enter_promiscuous_mode_generic(self, prefix, rate=RF_DATA_RATE['2m']):
#         self.send_usb_command(USB_COMMANDS['promiscuous_mode_generic'], [len(prefix), rate] + prefix)
#         self.dongle.read(0x81, 64, timeout=NRF24.usb_timeout)
#         # if len(prefix) > 0: logging.debug('Entered generic promiscuous mode with address prefix {0}'.format(
#         # ':'.join('{:02X}'.format(b) for b in prefix))) else: logging.debug('Entered promiscuous mode')
#
#     # Put the radio in ESB "sniffer" mode (ESB mode w/o auto-acking)
#     def enter_sniffer_mode(self, address):
#         self.send_usb_command(USB_COMMANDS['sniffer_mode'], [len(address)] + address)
#         self.dongle.read(0x81, 64, timeout=NRF24.usb_timeout)
#         # logging.debug('Entered sniffer mode with address {0}'.format(':'.join('{:02X}'.format(b) for b in address[
#         # ::-1])))
#
#     # Put the radio into continuous tone (TX) test mode
#     def enter_tone_test_mode(self):
#         self.send_usb_command(USB_COMMANDS['tone_test_mode'], [])
#         self.dongle.read(0x81, 64, timeout=NRF24.usb_timeout)
#         # logging.debug('Entered continuous tone test mode')
#
#     # Receive a payload if one is available
#     def receive_payload(self):
#         self.send_usb_command(USB_COMMANDS['receive_payload'], ())
#         return self.dongle.read(0x81, 64, timeout=NRF24.usb_timeout)
#
#     # Transmit a generic (non-ESB) payload
#     def transmit_payload_generic(self, payload, address=[0x33, 0x33, 0x33, 0x33, 0x33]):
#         data = [len(payload), len(address)] + payload + address
#         self.send_usb_command(USB_COMMANDS['transmit_payload_generic'], data)
#         return self.dongle.read(0x81, 64, timeout=NRF24.usb_timeout)[0] > 0
#
#     # Transmit an ESB payload
#     def transmit_payload(self, payload, timeout=4, retransmits=15):
#         data = [len(payload), timeout, retransmits] + payload
#         self.send_usb_command(USB_COMMANDS['transmit_payload'], data)
#         return self.dongle.read(0x81, 64, timeout=NRF24.usb_timeout)[0] > 0
#
#     # Transmit an ESB ACK payload
#     def transmit_ack_payload(self, payload):
#         data = [len(payload)] + payload
#         self.send_usb_command(USB_COMMANDS['transmit_ack_payload'], data)
#         return self.dongle.read(0x81, 64, timeout=NRF24.usb_timeout)[0] > 0
#
#     # Set the RF channel
#     def set_channel(self, channel):
#         if channel > 125:
#             channel = 125
#         self.send_usb_command(USB_COMMANDS['set_channel'], [channel])
#         self.dongle.read(0x81, 64, timeout=NRF24.usb_timeout)
#         # logging.debug('Tuned to {0}'.format(channel))
#
#     # Get the current RF channel
#     def get_channel(self):
#         self.send_usb_command(USB_COMMANDS['get_channel'], [])
#         return self.dongle.read(0x81, 64, timeout=NRF24.usb_timeout)
#
#     # Enable the LNA (CrazyRadio PA)
#     def enable_lna(self):
#         self.send_usb_command(USB_COMMANDS['enable_lan_pa'], [])
#         self.dongle.read(0x81, 64, timeout=NRF24.usb_timeout)
#
#     # Send a USB command
#     def send_usb_command(self, request, data):
#         data = [request] + list(data)
#         self.dongle.write(0x01, data, timeout=NRF24.usb_timeout)
#
#     # def reset(self):
#     #     USBDEVFS_RESET = ord('U') << (4 * 2) | 20
#     #     bus = str(self.dongle.bus).zfill(3)
#     #     addr = str(self.dongle.address).zfill(3)
#     #     filename = "/dev/bus/usb/%s/%s" % (bus, addr)
#     #     try:
#     #         ioctl(open(filename, "w"), USBDEVFS_RESET, 0)
#     #     except IOError:
#     #         print("Unable to reset device %s" % filename)
