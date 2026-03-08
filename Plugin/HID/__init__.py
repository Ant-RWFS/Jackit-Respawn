import os
import importlib

__all__ = []

current_dir = os.path.dirname(__file__)
for filename in os.listdir(current_dir):
    if filename.endswith('.py') and not filename.startswith('__'):
        module_name = filename[:-3]
        module = importlib.import_module(f'.{module_name}', __package__)
        if hasattr(module, 'HID'):
            hid_class = getattr(module, 'HID')
            globals()[module_name] = hid_class
            __all__.append(module_name)
