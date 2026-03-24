import flet as ft
from . import Appearance, Device, Plugin
from Script.Abstracts import AbstractUI


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
        for control in self.control.config_panels.controls:
            control.visible = False

    def update_config_menu_button(self, index):
        self.control.config_menu_buttons = self.control.updated_config_menu_button(index)
        self.control.config_menu.controls = self.control.config_menu_buttons
        self.control.config_menu.update()

    def switch_config_panel(self, index: int):
        self.reset_config_panel()
        self.update_config_menu_button(index)
        self.control.config_panels.controls[index].visible = True
        self.control.config_panels.update()


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
        self.selected_index = 0
        self.appearance_layout = Appearance.Panel().layout
        self.device_layout = Device.Panel().layout
        self.plugin_layout = Plugin.Panel().layout
        self.config_menu_buttons = self.init_config_menu_buttons()
        self.config_menu = self.init_config_menu()
        self.config_divider = self.init_config_divider()
        self.config_panels = self.init_config_panels()

    def init_config_menu_buttons(self):
        def menu_button(index, label):
            return ft.ElevatedButton(
                data={'index': index},
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=3.5)),
                content=ft.Text(
                    value=label,
                    theme_style=ft.TextThemeStyle.BODY_LARGE,
                    color=ft.Colors.PRIMARY if index != self.selected_index else ft.Colors.SURFACE,
                ),
                bgcolor=ft.Colors.TRANSPARENT if index != self.selected_index else ft.Colors.PRIMARY,
                on_click=lambda e, idx=index: self.panel.switch_config_panel(idx),
                width=150,
                height=60,
            )
        labels = self.config.RESC['text']['config']['menu']
        return [menu_button(0, labels['ap']),
                menu_button(1, labels['dv']),
                menu_button(2, labels['pg'])]

    def updated_config_menu_button(self, index):
        self.selected_index = index
        return self.init_config_menu_buttons()

    def init_config_menu(self):
        return ft.Column(
            controls=self.config_menu_buttons,
            spacing=5,
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
                self.device_layout,
                self.plugin_layout,
            ],
            alignment=ft.alignment.top_left,
            expand=True
        )
