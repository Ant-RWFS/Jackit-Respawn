import flet as ft
from Script.Data import USBEvent
from Script.Abstracts import AbstractUI
from Script.UI.Layout.Homepage.Signal import Diagram
from Script.UI.Layout.Homepage.Controls import *


class Panel(AbstractUI):
    def __init__(self):
        super().__init__()
        self.control = Control(self)
        self.layout = self.init_layout()

    def init_layout(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    self.control.output_window,
                    self.control.input_window,
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            alignment=ft.alignment.top_left,
            expand=True,
        )

    def toggle_recv_detail(self):
        self.control.device_recv_detail_window.visible = not self.control.device_recv_detail_window.visible
        self.control.device_recv_detail_window.update()

    def reset_recv_list(self, e):
        self.control.device_recv_list.controls.clear()
        self.control.reset_detail_header_icon()
        for key in self.control.device_recv_detail_dict:
            self.control.device_recv_detail_dict[key].value = '-'
        self.control.device_recv_data_diagram.visible = False
        self.page.update()

    def display_recv_detail(self, e, data, detail):
        self.control.selected_target = data

        if not self.control.device_recv_data_diagram.visible:
            self.control.device_recv_data_diagram.visible = True

        self.control.focus_detail_header_icon()
        for key, value in detail.items():
            if key == 'Data':
                self.control.device_recv_detail_dict['Hex Data'].value = value
                self.control.device_recv_detail_dict['Dec Data'].value = self.data_ft.hex_to_dec_string(value)
                self.control.data_diagram.update_diagram(self.data_ft.hex_string_to_dec_list(value))
            else:
                self.control.device_recv_detail_dict[key].value = value
        self.control.device_recv_header_bar = self.control.init_device_recv_header_bar()
        self.page.update()

    def copy_data_to_clipboard(self, e: ft.TapEvent, content):
        string = content.value
        if string != '-':
            string = self.data_ft.data_to_clipboard(string)
            self.page.set_clipboard(f'[{string}]')

    def update_attack_confirm_btn(self):
        self.control.attack_confirm_btn.update()

    def reset_attack_confirm_btn(self):
        self.control.attack_confirm_btn.reset()

    def scan_confirm(self, e):
        self.control.scan_confirm_btn.start_animation()
        if self.control.selected_vid_pid:
            if not self.control.scan_confirm_btn.layout.data:
                self.reset_attack_confirm_btn()
                self.control.scan_confirm_btn.update()
            else:
                self.reset_scan_confirm_btn()
            self.cmd.put({
                'type': 'scan_start' if self.control.scan_confirm_btn.layout.data else 'scan_stop',
                'vid': f'{self.control.selected_vid_pid[0]}',
                'pid': f'{self.control.selected_vid_pid[1]}',
                'devices': None,
                'payload': '',
                'mode': '',
                'config': self.config.RADIO_CONFIG_CACHE
                # 'mode': '',
                # 'parse': False,
                # 'language': 'us'
            })

    def reset_scan_confirm_btn(self):
        self.control.scan_confirm_btn.reset()

    def attack_confirm(self, e):
        if self.control.selected_vid_pid:
            payload = self.control.payload_input_window.value
            if not self.control.attack_confirm_btn.layout.data:
                self.reset_scan_confirm_btn()
                self.update_attack_confirm_btn()
            else:
                self.reset_attack_confirm_btn()
            self.payload_re_check(payload)
            payload = self.payload_reformat(payload)
            self.cmd.put({'type': 'attack_start' if self.control.attack_confirm_btn.layout.data else 'attack_stop',
                          'vid': f'{self.control.selected_vid_pid[0]}',
                          'pid': f'{self.control.selected_vid_pid[1]}',
                          'devices': self.control.selected_target,
                          'payload': payload,
                          'mode': f'{self.control.attack_mode_btn.layout.data}',
                          'config': self.config.RADIO_CONFIG_CACHE
                          # 'mode': f'{self.control.attack_mode_btn.layout.data}',
                          # 'parse': self.control.payload_mode_btn.data,
                          # 'language': f'{str(self.control.payload_language_btn.data).lower()}',
                          })

    def payload_re_check(self, payload):
        key = self.control.attack_mode_btn.layout.data
        mode_index = self.config.RADIO_CONFIG_CACHE[key]['mode_index']
        if mode_index == 0:
            if not self.data_ft.re_parse_payload(payload):
                return
        elif mode_index == 1:
            if not self.data_ft.re_raw_payload(payload):
                return
        # if  == 'Mousejack':
        #     if self.config.RADIO_CONFIG_CACHE['mj']['mode_index'] == 0:
        #         if not self.data_ft.re_parse_payload(payload):
        #             return
        #     else:
        #         if not self.data_ft.re_raw_payload(payload):
        #             return
        # else:

    #     if self.control.payload_mode_btn.data:
    #         if not self.data_ft.re_parse_payload(payload):
    #             return
    #     else:
    #         if not self.data_ft.re_raw_payload(payload):
    #             return

    def payload_reformat(self, payload):
        key = self.control.attack_mode_btn.layout.data
        mode_index = self.config.RADIO_CONFIG_CACHE[key]['mode_index']
        if mode_index == 0:
            return f'{payload}'
        else:
            return self.data_ft.raw_payload_to_list(payload)

    def display_diagram_dialog(self, e, diagram):
        dialog = ft.AlertDialog(
            modal=True,
            content=diagram,
            actions=[ft.TextButton(f"{self.config.RESC['text']['cancel']}",
                                   on_click=lambda e: self.page.close(dialog))],
            actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        )
        self.page.open(dialog)


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.selected_vid_pid = None
        self.selected_target = None
        self.panel = panel
        # Input Window
        self.payload_input_window = self.init_payload_input_window()
        # Action Bar
        self.reset_recv_btn = Button.ResetRecvButton(self.panel.reset_recv_list)
        self.payload_file_op_btn = Button.PayloadFileOPButton(self.payload_input_window)
        self.attack_mode_btn = Button.AttackModeButton()
        # self.payload_language_btn = self.init_payload_language_btn()
        # self.payload_mode_btn = self.init_payload_mode_btn()
        self.scan_confirm_btn = Button.ScanConfirmButton(self.panel.scan_confirm)
        self.attack_confirm_btn = Button.AttackConfirmButton(self.panel.attack_confirm)
        self.radio_setting_btn = Button.RadioSettingButton()
        self.payload_action_bar = self.init_payload_action_bar()
        # Output Views
        self.data_diagram = Diagram(self.page, self.config)
        self.device_recv_header_icon = self.init_device_recv_header_icon()
        self.device_recv_data_diagram = self.init_device_recv_data_diagram()
        self.device_recv_detail_dict = self.init_device_recv_detail_dict()
        self.device_recv_detail = self.init_device_recv_detail()

        self.device_recv_detail_window = self.init_device_recv_detail_window()
        self.device_recv_header_bar = self.init_device_recv_header_bar()
        self.device_recv_list = self.init_device_recv_list()
        self.device_recv_list_window = self.init_device_recv_list_window()

        self.device_output_window = self.init_device_output_window()
        # General Window Views
        self.output_window = self.init_output_window()
        self.input_window = self.init_input_window()
        self.subscribe_event()

    def subscribe_event(self):
        self.evt_bcst.subscribe(self.on_usb_receive, 'recv')
        self.evt_bcst.subscribe(self.on_scan_finish, 'scan_fin')
        self.evt_bcst.subscribe(self.on_attack_finish, 'atk_fin')
        self.evt_bcst.subscribe(self.on_error, 'error')

    def on_usb_receive(self, event: USBEvent):
        data = event.device['info']
        if data['device'] or data['payload']:
            data_dict = {
                'No.': len(self.device_recv_list.controls) + 1,
                'Timestamp': data['timestamp'],
                'Address': self.data_ft.form_hex_list(data['address'][::-1], ':'),
                'Channels': self.data_ft.form_list(data['channels'], ','),
                'HID': data['device'].description() if data['device'] else 'Unknown',
                'Data': self.data_ft.form_hex_list(data['payload'])
            }
            self.device_recv_list.controls.append(self.device_recv_data_bar(data, data_dict))
            self.page.update()

    def on_attack_finish(self, event: USBEvent):
        self.panel.reset_attack_confirm_btn()

    def on_scan_finish(self, event: USBEvent):
        self.panel.reset_scan_confirm_btn()

    def on_error(self, event: USBEvent):
        self.panel.reset_attack_confirm_btn()
        self.panel.reset_scan_confirm_btn()

    @staticmethod
    def attack_bar_sub_btn(icon, text, handler):
        return ft.MenuItemButton(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        name=icon,
                        scale=0.5,
                        color=ft.Colors.PRIMARY
                    ),
                    ft.Text(
                        value=text,
                        theme_style=ft.TextThemeStyle.LABEL_SMALL,
                    ),
                ],
                width=100,
            ),
            on_click=handler
        )

    @staticmethod
    def attack_bar_btn_text(text):
        return ft.Text(
            value=text,
            theme_style=ft.TextThemeStyle.BODY_SMALL,
            text_align=ft.TextAlign.CENTER,
            width=100,
        )

    # def init_payload_language_btn(self):
    #     texts = self.config.RESC['op']['attack']['language']
    #     current = 'us'
    #     return ft.SubmenuButton(
    #         data=current,
    #         content=self.attack_bar_btn_text(f"{texts['name']}: {current}"),
    #         controls=[
    #             self.attack_bar_sub_btn(None,
    #                                     str(name).upper(),
    #                                     lambda e, lang=name.lower():
    #                                     self.panel.set_payload_language(e, texts['name'], lang))
    #             for name in self.config.get_language_list()
    #         ],
    #     )
    #
    # def init_payload_mode_btn(self):
    #     texts = self.config.RESC['op']['attack']['payload']['mode']
    #     return ft.SubmenuButton(
    #         data=True,
    #         content=self.attack_bar_btn_text(f"{texts['name']}: {texts['ps']}"),
    #         controls=[
    #             self.attack_bar_sub_btn(ft.Icons.CODE, texts['ps'],
    #                                     lambda e: self.panel.set_payload_mode(e, texts['name'], texts['ps'])),
    #             self.attack_bar_sub_btn(ft.Icons.DATA_ARRAY, texts['rw'],
    #                                     lambda e: self.panel.set_payload_mode(e, texts['name'], texts['rw']))
    #         ],
    #     )

    def init_attack_confirm_btn(self):
        return ft.MenuItemButton(
            data=False,
            content=ft.Container(ft.Icon(
                name=ft.Icons.PLAY_CIRCLE_OUTLINE,
                color=ft.Colors.PRIMARY,
                scale=0.8
            ),
                width=100
            ),
            on_click=lambda e: self.panel.attack_confirm(e)
        )

    def init_payload_action_bar(self):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(self.reset_recv_btn.layout, expand=1),
                    ft.Container(self.payload_file_op_btn.layout, expand=1),
                    ft.Container(self.attack_mode_btn.layout, expand=1),
                    # self.payload_language_btn,
                    # self.payload_mode_btn,
                    ft.Container(self.scan_confirm_btn.layout, expand=1),
                    ft.Container(self.attack_confirm_btn.layout, expand=1),
                    ft.Container(self.radio_setting_btn.layout, expand=1)
                ],
                spacing=0
            ),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.PRIMARY)),
            expand=True,
        )

    def init_payload_input_window(self):
        return ft.TextField(
            multiline=True,
            max_lines=13,
            min_lines=13,
            border_radius=5,
            border_color=ft.Colors.TRANSPARENT,
            focused_border_color=ft.Colors.TRANSPARENT,
            hint_text=self.config.RESC['text']['hint']['payload']['enter'],
            hint_style=self.config.FIXED_STYLES['hint_text'],
            text_size=self.config.FONT['size']['medium'],
            expand=True
        )

    def init_input_window(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    self.payload_action_bar,
                    self.payload_input_window,
                ]
            ),
            border_radius=5,
            border=ft.border.all(
                width=1,
                color=ft.Colors.PRIMARY
            ),
            expand=True,
        )

    def init_device_recv_list_window(self):
        return ft.Container(
            ft.Column(
                controls=[
                    self.device_recv_header_bar,
                    self.device_recv_list
                ],
                spacing=0,
            ),
            padding=0,
            border_radius=5,
            border=ft.border.all(1, ft.Colors.PRIMARY),
            expand=2
        )

    def init_device_recv_detail_window(self):
        return ft.Container(
            content=self.device_recv_detail,
            padding=0,
            border_radius=5,
            border=ft.border.all(1, ft.Colors.PRIMARY),
            expand=1,
            visible=False
        )

    @staticmethod
    def init_device_recv_header_bar():
        def header(text, width=200, expand=False):
            return ft.Text(
                value=text,
                text_align=ft.TextAlign.CENTER,
                style=ft.TextThemeStyle.LABEL_SMALL,
                width=width,
                expand=expand
            )

        def divider():
            return ft.VerticalDivider(width=1,
                                      thickness=1)

        return ft.Container(
            ft.Row(
                controls=[
                    header('No.', width=40),
                    divider(),
                    header('Timestamp', width=100),
                    divider(),
                    header('Address', width=100),
                    divider(),
                    header('Channels', width=100),
                    divider(),
                    header('HID'),
                    divider(),
                    header('Data', expand=True),
                ],
                height=30,
                spacing=0,
            ),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.PRIMARY)),
        )

    @staticmethod
    def init_device_recv_list():
        return ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            expand=True,
        )

    def device_recv_data_bar(self, actual_data, display_data):
        format_data = self.format_device_data(actual_data)

        def device_recv_data(text, width=200, expand=False):
            return ft.Text(
                value=text,
                width=width,
                expand=expand,
                theme_style=ft.TextThemeStyle.LABEL_SMALL,
                text_align=ft.TextAlign.CENTER,
            )

        return ft.ElevatedButton(
            data=format_data,
            content=ft.Row(
                controls=[
                    device_recv_data(display_data['No.'], width=40),
                    device_recv_data(display_data['Timestamp'], width=100),
                    device_recv_data(display_data['Address'], width=100),
                    device_recv_data(display_data['Channels'], width=100),
                    device_recv_data(display_data['HID']),
                    device_recv_data(display_data['Data'], expand=True),
                ],
                spacing=0,
                height=40,
            ),
            style=ft.ButtonStyle(
                color=ft.Colors.PRIMARY,
                shape=ft.RoundedRectangleBorder(radius=0),
                padding=0,
            ),
            on_click=lambda e: self.panel.display_recv_detail(e, format_data, display_data)
        )

    @staticmethod
    def format_device_data(actual_data):
        address_bytes = actual_data['address']
        reversed_address = address_bytes[::-1]
        address_str = ':'.join(f'{b:02X}' for b in reversed_address)
        formatted_data = {
            address_str: {
                'index': actual_data['index'],
                'count': actual_data['count'],
                'timestamp': actual_data['timestamp'],
                'channels': actual_data['channels'],
                'address': actual_data['address'],
                'device': actual_data['device'],
                'payload': actual_data['payload']
            }
        }
        return formatted_data

    def init_device_recv_data_diagram(self):
        return ft.GestureDetector(content=self.data_diagram,
                                  on_tap=lambda e: self.panel.display_diagram_dialog(e, self.data_diagram),
                                  visible=False)

    @staticmethod
    def init_device_recv_header_icon():
        return ft.Icon(ft.Icons.GPS_NOT_FIXED)

    def focus_detail_header_icon(self):
        self.device_recv_header_icon.name = ft.Icons.CENTER_FOCUS_STRONG
        self.device_recv_header_icon.update()

    def reset_detail_header_icon(self):
        self.device_recv_header_icon.name = ft.Icons.GPS_NOT_FIXED
        self.device_recv_header_icon.update()

    def init_device_recv_detail(self):
        def divider():
            return ft.Divider(
                thickness=1,
                height=1
            )

        def header():
            return ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.device_recv_header_icon,
                            ft.Text(
                                value='Target',
                                theme_style=ft.TextThemeStyle.BODY_LARGE, text_align=ft.TextAlign.START,
                            )
                        ]
                    ),
                    divider()
                ],
                expand=True
            )

        def detail(text):
            content = self.device_recv_detail_dict[text]
            return ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(text,
                                            theme_style=ft.TextThemeStyle.LABEL_MEDIUM,
                                            text_align=ft.TextAlign.START,
                                            width=100),
                                    ft.IconButton(
                                        content=ft.Icon(ft.Icons.COPY, scale=0.8),
                                        on_click=lambda e: self.panel.copy_data_to_clipboard(e, content),
                                    ) if text in ['Hex Data', 'Dec Data'] else ft.Container()
                                ],
                                spacing=0,
                                width=140,
                                height=40
                            ),
                            content,
                        ]
                    )
                ],
                spacing=0,
            )

        def diagram():
            return ft.Column(
                controls=[
                    divider(),
                    ft.Text(value='Data Diagram',
                            theme_style=ft.TextThemeStyle.BODY_LARGE, text_align=ft.TextAlign.START, width=200),
                    self.device_recv_data_diagram
                ]
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    header(),
                    detail('No.'),
                    detail('Timestamp'),
                    detail('Address'),
                    detail('Channels'),
                    detail('HID'),
                    detail('Hex Data'),
                    detail('Dec Data'),
                    diagram()
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            padding=10,
            alignment=ft.alignment.top_left,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            expand=True
        )

    def init_device_recv_detail_dict(self):
        return {
            'No.': ft.Text('-'),
            'Timestamp': ft.Text('-'),
            'Address': ft.Text('-'),
            'Channels': ft.Text('-'),
            'HID': ft.Text('-'),
            'Hex Data': ft.Text('-', tooltip=self.config.RESC['text']['tooltip']['cc']),
            'Dec Data': ft.Text('-', tooltip=self.config.RESC['text']['tooltip']['cc'])
        }

    def init_device_output_window(self):
        return ft.Container(
            content=ft.Row(
                controls=[
                    self.device_recv_detail_window,
                    self.device_recv_list_window
                ]
            ),
            height=500,
            expand=True,
        )

    def init_output_window(self):
        return ft.Row(
            controls=[self.device_output_window],
            expand=True,
        )

    def update_current_usb_id(self, selected):
        self.selected_vid_pid = selected

    def update_current_usb_id_on_delete(self, selected):
        if selected == self.selected_vid_pid:
            self.selected_vid_pid = None
