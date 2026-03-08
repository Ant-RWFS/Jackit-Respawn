import flet as ft
from . import Appearance
from . import Firmware
from Script.Abstracts import AbstractUI

LABELS = ['Appearance', 'Firmware']


class Panel(AbstractUI):
    def __init__(self):
        super().__init__()
        self.control = Control(self)
        self.layout = self.init_layout()

    def init_layout(self):
        return ft.Row(
            controls=[
                self.control.config_menu,
                self.control.config_divider,
                self.control.config_panels,
            ],
            visible=False,
            expand=True
        )

    def reset_config_panel(self):
        for control in self.control.config_menu.controls:
            control.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=3.5),
            )
        for control in self.control.config_panels.controls:
            control.visible = False

    def switch_config_panel(self, index: int):
        self.reset_config_panel()
        self.control.config_menu.controls[index].style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=3.5),
        )
        self.control.config_menu.update()
        self.control.config_panels.controls[index].visible = True
        self.control.config_panels.update()


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
        self.appearance_layout = Appearance.Panel().layout
        self.firmware_layout = Firmware.Panel().layout
        self.config_menu = self.init_config_menu()
        self.config_divider = self.init_config_divider()
        self.config_panels = self.init_config_panels()

    def init_config_menu(self):
        return ft.Column(
            controls=[
                ft.ElevatedButton(
                    data=False
                    if index != 0
                    else True,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=3.5),
                    ),
                    content=ft.Text(
                        value=label,
                        theme_style=ft.TextThemeStyle.BODY_LARGE
                    ),
                    on_click=lambda e, idx=index: self.panel.switch_config_panel(idx),
                    width=150,
                    height=60,
                ) for index, label in enumerate(LABELS)
            ],
            spacing=0,
        )

    @staticmethod
    def init_config_divider():
        return ft.VerticalDivider(
            width=1,
            thickness=1,
        )

    def init_config_panels(self):
        return ft.Column(
            controls=[
                self.appearance_layout,
                self.firmware_layout,
            ],
            alignment=ft.alignment.top_left,
            expand=True
        )
