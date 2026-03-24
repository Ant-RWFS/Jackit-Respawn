import threading
import flet as ft
from Script.Data import USBEvent
from Script.Abstracts import AbstractUI
from Script.UI.Layout.Homepage.Singal import Diagram


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

    def reset_recv_list(self, e):
        self.control.device_recv_list.controls.clear()
        for key in self.control.device_recv_detail_dict:
            if key == 'Data Diagram':
                self.control.data_diagram.init_placeholder()
            else:
                self.control.device_recv_detail_dict[key].value = '-'
        self.control.device_recv_list.update()
        self.control.device_recv_detail.update()

    def display_recv_detail(self, e, data, detail):
        self.control.selected_device = data
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
        self.control.attack_confirm_btn.data = True
        self.control.attack_confirm_btn.content = ft.Container(ft.Icon(
            name=ft.Icons.PAUSE_CIRCLE_OUTLINE_OUTLINED,
            color=ft.Colors.PRIMARY,
            scale=0.8
        ),
            width=100
        )
        self.control.attack_confirm_btn.update()

    def reset_attack_confirm_btn(self):
        self.control.attack_confirm_btn.data = False
        self.control.attack_confirm_btn.content = ft.Container(ft.Icon(
            name=ft.Icons.PLAY_CIRCLE_OUTLINE,
            color=ft.Colors.PRIMARY,
            scale=0.8
        ),
            width=100
        )
        self.control.attack_confirm_btn.update()

    def set_attack_mode(self, e, name, mode):
        self.control.attack_mode_btn.content.value = f'{name}: {mode}'
        self.control.attack_mode_btn.data = mode
        self.page.update()

    def set_payload_language(self, e, name, language):
        self.control.payload_language_btn.content.value = f'{name}: {language}'
        self.control.payload_language_btn.data = language
        self.page.update()

    def set_payload_mode(self, e, name, mode):
        self.control.payload_mode_btn.data = True if mode == 'Parsed' else False
        self.control.payload_mode_btn.content = self.control.attack_bar_btn_text(f"{name}: {mode}")
        self.control.payload_mode_btn.update()

    def scan_confirm(self, e):
        self.start_animation()
        if self.control.selected_vid_pid:
            if not self.control.scan_confirm_btn.data:
                self.reset_attack_confirm_btn()
                self.update_scan_confirm_btn()
            else:
                self.reset_scan_confirm_btn()
            self.cmd.put({
                'type': 'scan_start' if self.control.scan_confirm_btn.data else 'scan_stop',
                'vid': f'{self.control.selected_vid_pid[0]}',
                'pid': f'{self.control.selected_vid_pid[1]}',
                'devices': None,
                'payload': '',
                'mode': '',
                'parse': False,
                'language': 'us'
            })

    def start_animation(self):
        if self.control.scan_confirm_btn.data:
            self.control.scan_confirm_btn.content.rotate = self.control.scan_confirm_btn.content.rotate + 0.5
            self.control.scan_confirm_btn.content.update()
            self.page.run_thread(threading.Timer(0.05, self.start_animation).start)

    def update_scan_confirm_btn(self):
        self.control.scan_confirm_btn.data = True
        self.control.scan_confirm_btn.content = ft.Container(ft.Icon(
            name=ft.Icons.RADAR,
            color=ft.Colors.PRIMARY,
            scale=0.8,
        ),
            width=100,
            rotate=0,
            animate_rotation=ft.animation.Animation(300, ft.AnimationCurve.LINEAR),
        )
        self.control.scan_confirm_btn.update()
        self.start_animation()

    def reset_scan_confirm_btn(self):
        self.control.scan_confirm_btn.data = False
        self.control.scan_confirm_btn.content = ft.Container(ft.Text(
            value=self.config.RESC['op']['attack']['confirm']['scn'],
            theme_style=ft.TextThemeStyle.LABEL_SMALL,
            text_align=ft.TextAlign.CENTER,
        ),
            width=100,
            rotate=0,
            animate_rotation=ft.animation.Animation(300, ft.AnimationCurve.LINEAR),
        )
        self.control.scan_confirm_btn.update()

    def attack_confirm(self, e):
        if self.control.selected_vid_pid:
            payload = self.control.payload_input_window.value
            if not self.control.attack_confirm_btn.data:
                self.reset_scan_confirm_btn()
                self.update_attack_confirm_btn()
            else:
                self.reset_attack_confirm_btn()
            self.payload_re_check(payload)
            payload = self.payload_reformat(payload)
            self.cmd.put({'type': 'attack_start' if self.control.attack_confirm_btn.data else 'attack_stop',
                          'vid': f'{self.control.selected_vid_pid[0]}',
                          'pid': f'{self.control.selected_vid_pid[1]}',
                          'devices': self.control.selected_device,
                          'payload': payload,
                          'mode': f'{self.control.attack_mode_btn.data}',
                          'parse': self.control.payload_mode_btn.data,
                          'language': f'{str(self.control.payload_language_btn.data).lower()}',
                          })

    def payload_re_check(self, payload):
        if self.control.payload_mode_btn.data:
            if not self.data_ft.re_parse_payload(payload):
                return
        else:
            if not self.data_ft.re_raw_payload(payload):
                return

    def payload_reformat(self, payload):
        if self.control.payload_mode_btn.data:
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
        self.selected_device = None
        self.panel = panel
        # Input Window
        self.payload_input_window = self.init_payload_input_window()
        # Action Bar
        self.recv_list_reset_btn = self.init_recv_list_reset_btn()
        self.attack_payload_btn = self.init_attack_payload_btn()
        self.attack_mode_btn = self.init_attack_mode_btn()
        self.payload_language_btn = self.init_payload_language_btn()
        self.payload_mode_btn = self.init_payload_mode_btn()
        self.scan_confirm_btn = self.init_scan_confirm_btn()
        self.attack_confirm_btn = self.init_attack_confirm_btn()
        self.payload_action_bar = self.init_payload_action_bar()
        # Output Views
        self.device_recv_header_bar = self.init_device_recv_header_bar()
        self.device_recv_list = self.init_device_recv_list()
        self.data_diagram = Diagram(self.page, self.config)
        self.device_recv_detail_dict = self.init_device_recv_detail_dict()
        self.device_recv_detail = self.init_device_recv_detail()
        self.device_recv_window = self.init_device_recv_window()
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

    def init_recv_list_reset_btn(self):
        return ft.MenuItemButton(
            data=False,
            content=ft.Container(ft.Text(
                value=self.config.RESC['op']['receive']['rt'],
                theme_style=ft.TextThemeStyle.LABEL_SMALL,
                text_align=ft.TextAlign.CENTER,
            ),
                width=100,
            ),
            on_click=lambda e: self.panel.reset_recv_list(e)
        )

    def init_attack_payload_btn(self):
        texts = self.config.RESC['op']['attack']['payload']
        return ft.SubmenuButton(
            content=self.attack_bar_btn_text(texts['name']),
            controls=[
                self.attack_bar_sub_btn(ft.Icons.FILE_DOWNLOAD_ROUNDED, texts['sv'],
                                        lambda e: self.file_op.save_file(e, texts['eg'], texts['ex'],
                                                                         self.payload_input_window)),
                self.attack_bar_sub_btn(ft.Icons.FILE_OPEN_ROUNDED, texts['op'],
                                        lambda e: self.file_op.open_file(e, texts['ex'],
                                                                         self.payload_input_window))
            ],
        )

    def init_attack_mode_btn(self):
        texts = self.config.RESC['op']['attack']['mode']
        return ft.SubmenuButton(
            data=texts['mj'],
            content=self.attack_bar_btn_text(f"{texts['name']}: {texts['mj']}"),
            controls=[
                self.attack_bar_sub_btn(ft.Icons.KEYBOARD_ROUNDED, texts['mj'],
                                        lambda e: self.panel.set_attack_mode(e, texts['name'], texts['mj'])),
                self.attack_bar_sub_btn(ft.Icons.REPLAY_ROUNDED, texts['rp'],
                                        lambda e: self.panel.set_attack_mode(e, texts['name'], texts['rp']))
            ],
        )

    def init_payload_language_btn(self):
        texts = self.config.RESC['op']['attack']['language']
        current = 'us'
        return ft.SubmenuButton(
            data=current,
            content=self.attack_bar_btn_text(f"{texts['name']}: {current}"),
            controls=[
                self.attack_bar_sub_btn(None,
                                        str(name).upper(),
                                        lambda e, lang=name.lower():
                                        self.panel.set_payload_language(e, texts['name'], lang))
                for name in self.config.get_language_list()
            ],
        )

    def init_payload_mode_btn(self):
        texts = self.config.RESC['op']['attack']['payload']['mode']
        return ft.SubmenuButton(
            data=True,
            content=self.attack_bar_btn_text(f"{texts['name']}: {texts['ps']}"),
            controls=[
                self.attack_bar_sub_btn(ft.Icons.CODE, texts['ps'],
                                        lambda e: self.panel.set_payload_mode(e, texts['name'], texts['ps'])),
                self.attack_bar_sub_btn(ft.Icons.DATA_ARRAY, texts['rw'],
                                        lambda e: self.panel.set_payload_mode(e, texts['name'], texts['rw']))
            ],
        )

    def init_scan_confirm_btn(self):
        return ft.MenuItemButton(
            data=False,
            content=ft.Container(ft.Text(
                value=self.config.RESC['op']['attack']['confirm']['scn'],
                theme_style=ft.TextThemeStyle.LABEL_SMALL,
                text_align=ft.TextAlign.CENTER,
            ),
                width=100,
                rotate=0,
                animate_rotation=ft.animation.Animation(300, ft.AnimationCurve.LINEAR),
            ),
            on_click=lambda e: self.panel.scan_confirm(e)
        )

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
                    self.recv_list_reset_btn,
                    self.attack_payload_btn,
                    self.attack_mode_btn,
                    self.payload_language_btn,
                    self.payload_mode_btn,
                    self.scan_confirm_btn,
                    self.attack_confirm_btn,
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

    def init_device_recv_window(self):
        return ft.Row(
            controls=[
                ft.Container(
                    ft.Column(
                        controls=[
                            self.device_recv_header_bar,
                            self.device_recv_list
                        ],
                        spacing=0,
                    ),
                    padding=0,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    border=ft.border.only(right=ft.BorderSide(1, ft.Colors.PRIMARY)),
                    expand=3
                ),
                ft.Container(
                    content=self.device_recv_detail,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    expand=2
                ),
            ],
            height=300,
            spacing=0,
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

    def init_device_recv_detail(self):
        def headline(text):
            content = self.device_recv_detail_dict[text]
            return ft.Column(
                controls=[
                    ft.Text(text, theme_style=ft.TextThemeStyle.BODY_LARGE, text_align=ft.TextAlign.CENTER),
                    ft.Container(ft.Divider(height=1, thickness=1, color=self.config.FIXED_COLORS['sub_content']),
                                 width=100),
                    ft.GestureDetector(
                        content=content,
                        on_tap=lambda e: self.panel.copy_data_to_clipboard(e, content)
                        if text in ['Hex Data', 'Dec Data'] else None,
                    ),
                ],
                spacing=0,
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    headline('No.'),
                    headline('Timestamp'),
                    headline('Address'),
                    headline('Channels'),
                    headline('HID'),
                    headline('Hex Data'),
                    headline('Dec Data'),
                    headline('Data Diagram')
                ],
                scroll=ft.ScrollMode.AUTO,
                width=1000,
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
            'Dec Data': ft.Text('-', tooltip=self.config.RESC['text']['tooltip']['cc']),
            'Data Diagram': ft.GestureDetector(content=self.data_diagram,
                                               on_tap=lambda e: self.panel.display_diagram_dialog(e, self.data_diagram))
        }

    def init_device_output_window(self):
        return ft.Container(
            content=self.device_recv_window,
            border_radius=5,
            border=ft.border.all(
                width=1,
                color=ft.Colors.PRIMARY
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
