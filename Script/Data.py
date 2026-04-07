import ast
import json
import re
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

    @staticmethod
    def hex_to_dec_string(hex_str, sep=' '):
        hex_bytes = hex_str.split()
        dec_bytes = [str(int(byte, 16)) for byte in hex_bytes]
        return sep.join(dec_bytes)

    @staticmethod
    def hex_string_to_dec_list(hex_string):
        hex_bytes = hex_string.split()
        return [int(byte, 16) for byte in hex_bytes]

    @staticmethod
    def data_to_clipboard(data: str):
        return data.replace(' ', ',')

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
                "dec": ",".join(f'{x}' for x in raw_data),
                "hex": ":".join(f"{x:02X}" for x in raw_data),
            }
        }
        return json.dumps(formatted_data, ensure_ascii=ensure_ascii, indent=indent, **kwargs)

    @staticmethod
    def truncate_text(text: str, max_length: int):
        return text[:max_length] + ('...' if len(text) > max_length else '')

    @staticmethod
    def validate_plugin(content, filename, plugin_type: str):
        validation_rules = {
            'Device': {
                'class_name': 'Driver',
                'required_methods': [
                    '__init__', 'init_device', 'execute_command',
                    'activate_promiscuous_mode', 'activate_promiscuous_mode_generic',
                    'activate_sniffer_mode', 'activate_tone_test_mode', 'recv_payload',
                    'send_payload', 'send_ack_payload', 'send_payload_generic',
                    'get_channel', 'set_channel', 'activate_LNA'
                ],
                'required_attributes': ['VENDOR_ID', 'PRODUCT_ID', 'ID'],
                'allowed_imports': ['usb', 'fcntl']
            },
            'HID': {
                'class_name': 'HID',
                'required_methods': [
                    '__init__', 'key', 'frame', 'build_frames', 'fingerprint', 'description'
                ],
                'required_attributes': [],
                'allowed_imports': []
            }
        }

        if plugin_type not in validation_rules:
            return False, f"Unknown plugin type: {plugin_type}"
        rules = validation_rules[plugin_type]

        try:
            tree = ast.parse(content)
            plugin_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == rules['class_name']:
                    plugin_class = node
                    break
            if not plugin_class:
                return False, f"Missing required class '{rules['class_name']}'"
            class_methods = [
                method.name for method in plugin_class.body
                if isinstance(method, ast.FunctionDef)
            ]
            missing_methods = [
                method for method in rules['required_methods']
                if method not in class_methods
            ]
            if missing_methods:
                return False, f"Missing required methods: {', '.join(missing_methods)}"
            if rules['required_attributes']:
                class_attributes = []
                for node in plugin_class.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                class_attributes.append(target.id)
                    elif isinstance(node, ast.AnnAssign):
                        if isinstance(node.target, ast.Name):
                            class_attributes.append(node.target.id)
                missing_attributes = [
                    attr for attr in rules['required_attributes']
                    if attr not in class_attributes
                ]
                if missing_attributes:
                    return False, f"Missing required class attributes: {', '.join(missing_attributes)}"
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            allowed_imports = rules['allowed_imports'] + ['.', '__future__']
            forbidden_imports = [
                imp for imp in imports
                if not imp.startswith('.') and imp not in allowed_imports
            ]
            if forbidden_imports:
                return False, f"Forbidden imports detected: {', '.join(forbidden_imports)}"
            return True, f"Valid {plugin_type} plugin"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"

    @staticmethod
    def re_parse_payload(payload):
        parse_re = r'^[^\x00-\x08\x0B\x0C\x0E-\x1F\x7F]+$'
        return re.match(parse_re, payload, re.DOTALL)

    def re_raw_payload(self, payload):
        raw_re = r'^[0-9\s,\[\]\n\r]+$'
        if not re.match(raw_re, payload, re.MULTILINE) or self.check_brackets_pair(payload) or self.check_brackets_pair(
                payload):
            return False
        else:
            return True

    @staticmethod
    def check_brackets_pair(text):
        stack = []
        for i, char in enumerate(text):
            if char == '[':
                stack.append((char, i))
            elif char == ']':
                if not stack:
                    return False
                stack.pop()
        if stack:
            return False
        return True

    @staticmethod
    def check_array_structure(text):
        text = text.strip()
        if ('[' not in text or ']' not in text) or not text.startswith('[') or not text.endswith(']'):
            return False
        else:
            return True

    @staticmethod
    def raw_payload_to_list(payload):
        if not payload or not isinstance(payload, str):
            return []

        try:
            cleaned = re.sub(r'\s', '', payload)
            result = []
            i = 0
            while i < len(cleaned):
                if cleaned[i] == '[':
                    j = i + 1
                    bracket_count = 1
                    while j < len(cleaned) and bracket_count > 0:
                        if cleaned[j] == '[':
                            bracket_count += 1
                        elif cleaned[j] == ']':
                            bracket_count -= 1
                        j += 1
                    if bracket_count == 0:
                        array_content = cleaned[i + 1:j - 1]
                        current_array = []
                        if array_content:
                            for num_str in array_content.split(','):
                                num_str = num_str.strip()
                                if not num_str:
                                    continue
                                if num_str.isdigit():
                                    num = int(num_str)
                                    if 0 <= num <= 255:
                                        current_array.append(num)
                                    else:
                                        current_array.append(255)
                                else:
                                    current_array.append(0)
                        if current_array:
                            result.append(current_array)
                        i = j
                    else:
                        i += 1
                else:
                    i += 1
            return result
        except Exception as e:
            return []
