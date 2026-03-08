import flet as ft
from . import DeviceOperator
from Script.Abstracts import AbstractUI
from Script.Data import USBEvent


class Panel(AbstractUI):
    def __init__(self):
        super().__init__()
        self.control = Control(self)
        self.layout = self.init_layout()

    def init_layout(self):
        return ft.Row(
            controls=[
                self.control.device_info_view,
                self.control.device_op_layout,
            ],
            visible=True,
            expand=True
        )


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
        # Device Info
        self.device_cards = {}
        self.device_info_width = 0
        self.selected_vid_pid = None
        self.is_device_info_expanded = False
        self.device_info_empty_hint = self.init_device_info_empty_hint()
        self.device_info_display_btn = self.init_device_info_display_btn()
        self.device_info_btn_list = self.init_device_info_btn_list()
        self.device_info_view = self.init_device_info_view()
        # Device Operation
        self.device_op = DeviceOperator.Panel()
        self.device_op_layout = self.device_op.layout

        self.evt_bcst.subscribe(self.on_usb_event)

    def init_device_info_empty_hint(self):
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.Icons.REPORT_PROBLEM,
                            color=self.config.FIXED_COLORS['warning'],
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Text(
                    value=self.config.RESC['text']['hint']['device']['info']['empty'],
                    theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                    color=self.config.FIXED_COLORS['warning'],
                    text_align=ft.TextAlign.CENTER,
                )
            ],
        )

    def init_device_info_display_btn(self):
        return ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.MENU,
                tooltip=self.config.RESC['text']['hint']['device']['info']['hide'],
                on_click=self.toggle_sidebar,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            ),
            border=ft.Border(right=ft.BorderSide(3, ft.Colors.PRIMARY)),
            border_radius=3,
        )

    def init_device_info_view(self):
        return ft.Row(
            controls=[
                ft.Column(controls=[self.device_info_btn_list]),
                ft.Container(
                    content=ft.Column(
                        controls=[self.device_info_display_btn],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    border=ft.Border(left=ft.BorderSide(1, ft.Colors.PRIMARY)),
                ),
            ],
        )

    def init_device_info_btn_list(self):
        return ft.ListView(
            controls=[self.device_info_empty_hint],
            width=180 if self.is_device_info_expanded else 0,
            spacing=5,
            padding=10,
            expand=True,
            visible=True if self.is_device_info_expanded else False,
        )

    def toggle_sidebar(self, e):
        self.is_device_info_expanded = not self.is_device_info_expanded
        self.device_info_btn_list.visible = self.is_device_info_expanded

        if self.is_device_info_expanded:
            self.device_info_btn_list.width = 180
            self.device_info_display_btn.content.icon = ft.Icons.CHEVRON_LEFT
        else:
            self.device_info_btn_list.width = 0
            self.device_info_display_btn.content.icon = ft.Icons.MENU

        self.page.update()

    def registered_usb_button(self, vid, pid):
        # is_selected = self.selected_vid_pid == (vid, pid)
        return ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.USB),
                    ft.Text(
                        value='USB',
                        theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM
                    ),
                    ft.Text(
                        value=f"VID: {str(vid).zfill(4).upper()}\n"
                              f"PID: {str(pid).zfill(4).upper()}",
                        theme_style=ft.TextThemeStyle.BODY_SMALL
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
            ),
            height=60,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=lambda e, v=vid, p=pid: self.on_device_selected(v, p),
        )

    def on_device_selected(self, vid, pid):
        self.selected_vid_pid = (vid, pid)
        self.device_op.control.update_current_usb_id(self.selected_vid_pid)
        self.refresh_buttons()
        self.page.update()

    def refresh_buttons(self):
        for (vid, pid), button in self.device_cards.items():
            new_button = self.registered_usb_button(vid, pid)
            index = self.device_info_btn_list.controls.index(button)
            self.device_info_btn_list.controls[index] = new_button
            self.device_cards[(vid, pid)] = new_button

    def on_usb_event(self, event: USBEvent):
        event_type = event.type
        vid = event.device['vendor_id']
        pid = event.device['product_id']

        if event_type == 'add':
            self.on_usb_add(vid, pid)
        elif event_type == 'remove':
            self.on_usb_remove(vid, pid)
        self.page.update()

    def on_usb_add(self, vid, pid):
        new_button = self.registered_usb_button(vid, pid)
        self.selected_vid_pid = (vid, pid)
        self.device_op.control.update_current_usb_id(self.selected_vid_pid)
        self.device_cards[(vid, pid)] = new_button
        self.device_info_btn_list.controls.append(new_button)
        if self.device_cards and self.device_info_empty_hint in self.device_info_btn_list.controls:
            self.device_info_btn_list.controls.remove(self.device_info_empty_hint)

    def on_usb_remove(self, vid, pid):
        key = (vid, pid)
        if key in self.device_cards:
            button = self.device_cards[key]
            if button in self.device_info_btn_list.controls:
                self.device_info_btn_list.controls.remove(button)
                self.device_op.control.update_current_usb_id_on_delete(key)
            del self.device_cards[key]
            if not (self.device_cards or self.device_info_empty_hint in self.device_info_btn_list.controls):
                self.device_info_btn_list.controls.append(self.device_info_empty_hint)
