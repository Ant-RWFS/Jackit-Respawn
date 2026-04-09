import flet as ft
from . import Workbench, Intro
from Script.Abstracts import AbstractUI
from Script.Data import USBEvent


class Panel(AbstractUI):
    def __init__(self):
        super().__init__()
        self.workbench = Workbench.Panel()
        self.intro = Intro.Panel(self.workbench)
        self.layout = self.init_layout()

    def init_layout(self):
        return ft.Stack(
            controls=[
                self.workbench.layout,
                self.intro.layout,
            ],
            expand=True,
        )


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
        self.subscribe_event()

    def subscribe_event(self):
        self.evt_bcst.subscribe(self.on_usb_event, ['add', 'remove', 'offline'])
        self.evt_bcst.subscribe(self.on_error_event, 'error')

    def on_usb_event(self, event: USBEvent):
        self.panel.page.open(
            ft.SnackBar(
                content=ft.Text(
                    value=f"{self.config.RESC['text']['hint']['usb'][event.type]} "
                          f"VendorId:{event.device['vendor_id']} ProductId:{event.device['product_id']}",
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=self.config.FIXED_COLORS['warning'] if event.type == 'offline' else ft.Colors.PRIMARY,
                duration=2000,
            )
        )

    def on_error_event(self, event: USBEvent):
        self.panel.page.open(
            ft.SnackBar(
                content=ft.Text(
                    value=event.device['info'],
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=self.config.FIXED_COLORS['error'],
                duration=5000,
            )
        )
