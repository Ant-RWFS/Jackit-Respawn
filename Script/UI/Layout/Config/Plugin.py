import flet as ft
from Script.Abstracts import AbstractUI

CONFIGS_ITEMS = {
    'HID': ['Fingerprint', 'Registry'],
    'Device': ['Driver', 'Registry']
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
                    self.control.fpr_list_window,
                    self.control.fpr_registry_config,
                    self.control.plugin_divider,
                    self.control.plugin_bodies[1],
                    self.control.driver_list_window,
                    self.control.driver_registry_config
                ],
                alignment=ft.alignment.top_left,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            visible=False,
            expand=True
        )

    def display_registered_plugin(self, e, dict_name, file_name):
        dialog = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            value=file_name,
                            style=ft.TextThemeStyle.TITLE_LARGE,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(
                            content=ft.Text(
                                value='\n'.join(self.config.read_plugin(dict_name, file_name)),
                                selectable=True,
                            ),
                            expand=True
                        )
                    ],
                    spacing=10,
                ),
                expand=True
            ),
            actions=[
                ft.TextButton(
                    text=f"{self.config.RESC['text']['cancel']}",
                    on_click=lambda e: self.page.close(dialog)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        )
        self.page.open(dialog)

    def register_plugin(self, e, dict_name, callback):
        self.file_op.import_plugin_file(e, dict_name, callback)
        self.reload_device()

    def delete_plugin_confirm(self, e, dict_name, file_name, callback):
        dialog = ft.AlertDialog(
            modal=True,
            content=ft.Text(f"{self.config.RESC['text']['delete']['content']} {CONFIGS_ITEMS[dict_name][0]} plugin: "
                            f"'{file_name}' ?"),
            actions=[
                ft.TextButton(f"{self.config.RESC['text']['cancel']}",
                              on_click=lambda e: self.page.close(dialog)),
                ft.TextButton(f"{self.config.RESC['text']['confirm']}",
                              on_click=lambda e: self.delete_plugin(e, dict_name, file_name, dialog,
                                                                    callback))
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        self.page.open(dialog)

    def delete_plugin(self, e, dict_name, file_name, dialog, callback=None):
        self.file_op.delete_plugin_file(dict_name, file_name, callback)
        self.reload_device()
        self.page.close(dialog)

    def reload_device(self):
        self.cmd.put({
            'type': 'reload_device',
            'vid': '',
            'pid': '',
            'devices': None,
            'payload': '',
            'mode': '',
            'parse': False,
            'language': 'us'
        })


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
        self.plugin_dicts = list(CONFIGS_ITEMS.keys())
        self.plugin_divider = self.init_plugin_divider()
        self.plugin_bodies = self.init_plugin_bodies()
        self.plugin_labels = self.init_plugin_labels()
        self.fpr_list = self.init_fpr_list()
        self.fpr_list_window = self.init_fpr_list_window()
        self.fpr_registry_button = self.init_fpr_registry_button()
        self.fpr_registry_config = self.init_fpr_registry_config()
        self.driver_list = self.init_driver_list()
        self.driver_list_window = self.init_driver_list_window()
        self.driver_registry_button = self.init_driver_registry_button()
        self.driver_registry_config = self.init_driver_registry_config()

    @staticmethod
    def init_plugin_divider():
        return ft.Container(
            content=ft.Divider(
                height=10,
                thickness=1.5,
            ),
            width=300,
        )

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
        dict_name = self.plugin_dicts[0]
        return ft.Column(
            controls=[
                ft.TextButton(
                    content=ft.Text(
                        value=self.data_ft.truncate_text(hid, 15),
                        theme_style=ft.TextThemeStyle.LABEL_SMALL,
                    ),
                    width=200,
                    style=self.config.FIXED_STYLES['list_button'],
                    on_click=lambda e, file_name=hid: self.panel.display_registered_plugin(e, dict_name, file_name),
                    on_long_press=lambda e, file_name=hid: self.panel.delete_plugin_confirm(e, dict_name, file_name,
                                                                                            self.reset_hid_list)
                )
                for hid in self.config.PLUGIN['hid']
            ],
            scroll=ft.ScrollMode.ALWAYS,
        )

    def init_fpr_list(self):
        return ft.Container(
            content=self.hid_list_content(),
            height=100,
            border=ft.border.all(1, ft.Colors.PRIMARY),
            border_radius=5
        )

    def reset_hid_list(self):
        self.config.reload_plugin()
        self.fpr_list.content = self.hid_list_content()
        self.fpr_list.update()

    def init_fpr_list_window(self):
        return ft.Row(
            controls=[
                self.plugin_labels['HID'][0],
                self.fpr_list
            ],
            vertical_alignment=ft.CrossAxisAlignment.START
        )

    def init_fpr_registry_button(self):
        dict_name = self.plugin_dicts[0]
        return ft.IconButton(
            icon=ft.Icons.FINGERPRINT,
            scale=0.8,
            width=200,
            style=self.config.FIXED_STYLES['icon_button'],
            on_click=lambda e: self.panel.register_plugin(e, dict_name, self.reset_hid_list)
        )

    def init_fpr_registry_config(self):
        return ft.Row(
            controls=[
                self.plugin_labels['HID'][1],
                self.fpr_registry_button
            ]
        )

    def driver_list_content(self):
        dict_name = self.plugin_dicts[1]
        return ft.Column(
            controls=[
                ft.TextButton(
                    content=ft.Text(
                        value=self.data_ft.truncate_text(driver, 15),
                        theme_style=ft.TextThemeStyle.LABEL_SMALL,
                    ),
                    width=200,
                    style=self.config.FIXED_STYLES['list_button'],
                    on_click=lambda e, file_name=driver: self.panel.display_registered_plugin(e, dict_name, file_name),
                    on_long_press=lambda e, file_name=driver: self.panel.delete_plugin_confirm(e, dict_name, file_name,
                                                                                               self.reset_driver_list)
                )
                for driver in self.config.PLUGIN['device']
            ],
            scroll=ft.ScrollMode.ALWAYS,
        )

    def init_driver_list(self):
        return ft.Container(
            content=self.driver_list_content(),
            height=100,
            border=ft.border.all(1, ft.Colors.PRIMARY),
            border_radius=5
        )

    def reset_driver_list(self):
        self.config.reload_plugin()
        self.driver_list.content = self.driver_list_content()
        self.driver_list.update()

    def init_driver_list_window(self):
        return ft.Row(
            controls=[
                self.plugin_labels['Device'][0],
                self.driver_list
            ],
            vertical_alignment=ft.CrossAxisAlignment.START
        )

    def init_driver_registry_button(self):
        dict_name = self.plugin_dicts[1]
        return ft.IconButton(
            icon=ft.Icons.SETTINGS_INPUT_COMPONENT,
            scale=0.8,
            width=200,
            style=self.config.FIXED_STYLES['icon_button'],
            on_click=lambda e: self.panel.register_plugin(e, dict_name, self.reset_driver_list)
        )

    def init_driver_registry_config(self):
        return ft.Row(
            controls=[
                self.plugin_labels['Device'][1],
                self.driver_registry_button
            ]
        )
