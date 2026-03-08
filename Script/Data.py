import json
import time
from dataclasses import dataclass
from datetime import datetime


@dataclass
class USBEvent:
    type: str
    device: dict
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class Formatter:
    def __init__(self):
        pass

    @staticmethod
    def form_list(data, sep=' '):
        return sep.join(f'{item}' for item in list(data))

    @staticmethod
    def form_hex_list(data, sep=' '):
        return sep.join(f'{item:02X}' for item in list(data))

    def form_address_list(self, address_list, sep=' '):
        hex_address_list = []
        for address in list(address_list):
            hex_address_list.append(self.form_hex_list(address[::-1], ':'))
        return self.form_list(hex_address_list, sep)

    def form_channels_list(self, channels_list, sep=' '):
        formed_channels_list = []
        for channel in list(channels_list):
            formed_channels_list.append(self.form_list(channel, ' | '))
        return self.form_list(formed_channels_list, sep)

    def form_hid_list(self, hid_list, sep=' '):
        formed_hid_list = []
        for hid in list(hid_list):
            formed_hid_list.append(hid.description() if hid.description() else 'Unknown')
        return self.form_list(formed_hid_list, sep)

    @staticmethod
    def form_timestamp_str_in_hour():
        return str(datetime.fromtimestamp(time.time()).strftime('%H:%M:%S'))

    @staticmethod
    def form_timestamp_str_in_date():
        return str(datetime.fromtimestamp(time.time()).strftime('%m-%d %H:%M:%S'))

    @staticmethod
    def form_timestamp_str_in_year():
        return str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

    @staticmethod
    def dict_to_json(data, ensure_ascii=False, indent=2, **kwargs):
        return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent, **kwargs)

    @staticmethod
    def raw_data_to_json(raw_data, ensure_ascii=False, indent=2, **kwargs):
        formatted_data = {
            "raw_data": {
                "dec": "," .join(f'{x}' for x in raw_data),
                "hex": ":".join(f"{x:02X}" for x in raw_data),
            }
        }
        return json.dumps(formatted_data, ensure_ascii=ensure_ascii, indent=indent, **kwargs)
