class InputReport(object):
    def __init__(self):
        self.payloads = []
        self.initial_checksum = [0, 0xff]
        self.duplicates = []
        self.template_payloads = []
        self.template_specials = []

    def add_payload(self, payload):
        self.payloads.append(payload)

    def add_duplicates(self, duplicates):
        self.duplicates.append(duplicates)

    def add_template_payload(self, template_payload):
        self.template_payloads.append(template_payload)

    def add_template_special(self, template_special):
        self.template_specials.append(template_special)


class OutputReport(object):
    def __init__(self):
        self.report = []
        self.address = []
        self.vendor = ""
        self.checksum = 0
        self.index = {
            "key": {
                "hid": 0,
                "mod": 0
            },
            "checksum": -1
        }
        self.template_payloads = []
        self.template_specials = []

    def set_report(self, report):
        self.report = report

    def set_address(self, address):
        self.address = address

    def set_vendor(self, vendor):
        self.vendor = vendor

    def set_checksum(self, checksum):
        self.checksum = checksum

    def set_index_key(self, hid, mod):
        self.index["key"]["hid"] = hid
        self.index["key"]["mod"] = mod

    def set_index_key_HID(self, hid):
        self.index["key"]["hid"] = hid

    def set_index_key_MOD(self, mod):
        self.index["key"]["mod"] = mod

    def set_index_key_checksum(self, checksum):
        self.index["checksum"] = checksum

    def add_template_payload(self, template_payload):
        self.template_payloads.append(template_payload)

    def remove_template_payload(self, template_payload):
        self.template_payloads.remove(template_payload)

    def add_template_special(self, template_special):
        self.template_specials.append(template_special)

    def remove_template_special(self, template_special):
        self.template_specials.remove(template_special)
