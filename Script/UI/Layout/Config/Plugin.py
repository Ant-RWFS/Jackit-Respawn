import flet as ft
from Script.Abstracts import AbstractUI

CONFIGS_ITEMS = {
    'HID': ['Fingerprints', 'Registry']
}


class Panel(AbstractUI):
    def __init__(self):
        super().__init__()
        self.control = Control(self)
        self.layout = self.init_layout()

    def init_layout(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    self.control.plugin_bodies[0],
                    self.control.hid_list_window,
                    self.control.plugin_registry_config
                ],
                alignment=ft.alignment.top_left,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            visible=False,
            expand=True
        )

    def display_registered_hid(self, e, hid):
        dialog = ft.AlertDialog(
            modal=True,
            content=ft.Text(
                value='\n'.join(self.config.read_hid_plugin(hid)),
                selectable=True
            ),
            actions=[
                ft.TextButton(
                    text=f"{self.config.RESC['text']['cancel']}",
                    on_click=lambda e: self.page.close(dialog))
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        )
        self.page.open(dialog)

    def register_hid_plugin(self, e):
        self.file_op.import_hid_plugin_file(e, callback=self.control.reset_hid_list)

    def delete_hid_plugin_confirm(self, e, hid):
        dialog = ft.AlertDialog(
            modal=True,
            content=ft.Text(f"{self.config.RESC['text']['delete']['content']} HID plugin: "
                            f"'{hid}' ?"),
            actions=[
                ft.TextButton(f"{self.config.RESC['text']['cancel']}",
                              on_click=lambda e: self.page.close(dialog)),
                ft.TextButton(f"{self.config.RESC['text']['confirm']}",
                              on_click=lambda e: self.delete_hid_plugin(e, hid, dialog))
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        self.page.open(dialog)

    def delete_hid_plugin(self, e, hid, dialog):
        self.file_op.delete_hid_plugin_file(hid, callback=self.control.reset_hid_list)
        self.page.close(dialog)


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
        self.plugin_bodies = self.init_plugin_bodies()
        self.plugin_labels = self.init_plugin_labels()
        self.hid_list = self.init_hid_list()
        self.hid_list_window = self.init_hid_list_window()
        self.hid_registry_button = self.init_plugin_registry_button()
        self.plugin_registry_config = self.init_plugin_registry_config()

    @staticmethod
    def init_plugin_bodies():
        return [
            ft.Text(
                value=label,
                style=ft.TextThemeStyle.BODY_MEDIUM,
                width=80,
                height=20,
            ) for label in CONFIGS_ITEMS.keys()
        ]

    @staticmethod
    def init_plugin_labels():
        return {
            category: [
                ft.Text(
                    value=item,
                    style=ft.TextThemeStyle.LABEL_SMALL,
                    width=80,
                )
                for item in items
            ]
            for category, items in CONFIGS_ITEMS.items()
        }

    def hid_list_content(self):
        return ft.Column(
                controls=[
                    ft.TextButton(
                        content=ft.Text(
                            value=self.data_ft.truncate_text(hid, 15),
                            theme_style=ft.TextThemeStyle.LABEL_SMALL,
                        ),
                        width=200,
                        style=self.config.FIXED_STYLES['list_button'],
                        on_click=lambda e: self.panel.display_registered_hid(e, hid),
                        on_long_press=lambda e: self.panel.delete_hid_plugin_confirm(e, hid)
                    )
                    for hid in self.config.PLUGIN['hid']
                ],
                scroll=ft.ScrollMode.ALWAYS,
            )

    def init_hid_list(self):
        return ft.Container(
            content=self.hid_list_content(),
            height=100,
            border=ft.border.all(1, ft.Colors.PRIMARY),
            border_radius=5
        )

    def reset_hid_list(self):
        self.config.reload_plugin()
        self.hid_list.content = self.hid_list_content()
        self.hid_list.update()

    def init_hid_list_window(self):
        return ft.Row(
            controls=[
                self.plugin_labels['HID'][0],
                self.hid_list
            ],
            vertical_alignment=ft.CrossAxisAlignment.START
        )

    def init_plugin_registry_button(self):
        return ft.IconButton(
            icon=ft.Icons.FINGERPRINT,
            scale=0.8,
            width=200,
            style=self.config.FIXED_STYLES['icon_button'],
            on_click=lambda e: self.panel.register_hid_plugin(e)
        )

    def init_plugin_registry_config(self):
        return ft.Row(
            controls=[
                self.plugin_labels['HID'][1],
                self.hid_registry_button
            ]
        )
