import threading
import flet as ft
from Script.Abstracts import AbstractUI
from Script.UI.Layout.Config.Radio import Panel as RadioConfigPanel


def attack_bar_btn_text(text):
    return ft.Text(
        value=text,
        theme_style=ft.TextThemeStyle.BODY_SMALL,
        text_align=ft.TextAlign.CENTER,
        width=200,
    )


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
            width=200,
        ),
        on_click=handler
    )


class ResetRecvButton(AbstractUI):
    def __init__(self, func):
        super().__init__()
        self.func = func
        self.layout = self.init_layout()

    def init_layout(self):
        return ft.SubmenuButton(
            data=False,
            content=ft.MenuItemButton(
                content=ft.Text(
                    value=self.config.RESC['op']['receive']['rt'],
                    theme_style=ft.TextThemeStyle.LABEL_SMALL,
                    text_align=ft.TextAlign.CENTER,
                ),
                on_click=lambda e: self.func(e),
            ),
        )


class PayloadFileOPButton(AbstractUI):
    def __init__(self, payload_input_window):
        super().__init__()
        self.payload_input_window = payload_input_window
        self.layout = self.init_layout()

    def init_layout(self):
        texts = self.config.RESC['op']['attack']['payload']
        return ft.SubmenuButton(
            content=attack_bar_btn_text(texts['name']),
            controls=[
                attack_bar_sub_btn(ft.Icons.FILE_DOWNLOAD_ROUNDED, texts['sv'],
                                   lambda e: self.file_op.save_file(e, texts['eg'], texts['ex'],
                                                                    self.payload_input_window)),
                attack_bar_sub_btn(ft.Icons.FILE_OPEN_ROUNDED, texts['op'],
                                   lambda e: self.file_op.open_file(e, texts['ex'],
                                                                    self.payload_input_window))
            ],
        )


class AttackModeButton(AbstractUI):
    def __init__(self):
        super().__init__()
        self.layout = self.init_layout()

    def init_layout(self):
        texts = self.config.RESC['op']['attack']['mode']
        return ft.SubmenuButton(
            data='mj',
            content=attack_bar_btn_text(f"{texts['name']}: {texts['mj']}"),
            controls=[
                attack_bar_sub_btn(ft.Icons.KEYBOARD_ROUNDED, texts['mj'],
                                   lambda e: self.set(e, texts['name'], texts['mj'], 'mj')),
                attack_bar_sub_btn(ft.Icons.REPLAY_ROUNDED, texts['rp'],
                                   lambda e: self.set(e, texts['name'], texts['rp'], 'rp'))
            ],
        )

    def set(self, e, name, mode, key):
        self.layout.content.value = f'{name}: {mode}'
        self.layout.data = key
        self.layout.update()


class RadioSettingButton(AbstractUI):
    def __init__(self):
        super().__init__()
        self.radio_config = RadioConfigPanel()
        self.layout = self.init_layout()

    def init_layout(self):
        return ft.SubmenuButton(
            content=ft.MenuItemButton(
                content=ft.Icon(
                    ft.Icons.SETTINGS,
                    color=ft.Colors.PRIMARY,
                    scale=0.8
                ),
                on_click=lambda e: self.open_attack_setting_dialog(e),
            )
        )

    def open_attack_setting_dialog(self, e):
        self.page.open(self.setting_dialog())

    def setting_dialog(self):
        dialog = ft.AlertDialog(
            modal=True,
            content=self.radio_config.config_layout,
            actions=[
                ft.TextButton(
                    text=f"{self.config.RESC['text']['discard']}",
                    on_click=lambda e: self.page.close(dialog),
                    style=self.config.FIXED_STYLES['normal_color_button'],
                    width=200
                ),
                ft.TextButton(
                    text=f"{self.config.RESC['text']['save']}",
                    on_click=lambda e: self.radio_config.save_radio_config(e),
                    style=self.config.FIXED_STYLES['invert_color_button'],
                    width=200
                )
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY
        )
        return dialog


class ScanConfirmButton(AbstractUI):
    def __init__(self, func):
        super().__init__()
        self.func = func
        self.layout = self.init_layout()
        self.icon_ref = None

    def init_layout(self):
        return ft.SubmenuButton(
            data=False,
            content=ft.MenuItemButton(
                content=ft.Text(
                    value=self.config.RESC['op']['attack']['confirm']['scn'],
                    theme_style=ft.TextThemeStyle.LABEL_SMALL,
                    text_align=ft.TextAlign.CENTER,
                ),
                on_click=lambda e: self.func(e),
            ),
        )

    def start_animation(self):
        if self.layout.data and self.icon_ref:
            self.icon_ref.rotate = (self.icon_ref.rotate or 0) + 0.5
            self.icon_ref.update()
            self.page.run_thread(threading.Timer(0.05, self.start_animation).start)

    def update(self):
        self.layout.data = True
        self.icon_ref = ft.Icon(
            name=ft.Icons.RADAR,
            color=ft.Colors.PRIMARY,
            scale=0.8,
        )
        self.layout.content.content = self.icon_ref
        self.layout.update()
        self.start_animation()

    def reset(self):
        self.layout.data = False
        self.icon_ref = None
        self.layout.content.content = ft.Text(
            value=self.config.RESC['op']['attack']['confirm']['scn'],
            theme_style=ft.TextThemeStyle.LABEL_SMALL,
            text_align=ft.TextAlign.CENTER,
        )
        self.layout.update()


class AttackConfirmButton(AbstractUI):
    def __init__(self, func):
        super().__init__()
        self.func = func
        self.layout = self.init_layout()

    def init_layout(self):
        return ft.SubmenuButton(
            data=False,
            content=ft.MenuItemButton(
                content=ft.Icon(
                    name=ft.Icons.PLAY_CIRCLE_OUTLINE,
                    color=ft.Colors.PRIMARY,
                    scale=0.8
                ),
                on_click=lambda e: self.func(e),
            ),
        )

    def update(self):
        self.layout.data = True
        self.layout.content.content = ft.Icon(
            name=ft.Icons.PAUSE_CIRCLE_OUTLINE_OUTLINED,
            color=ft.Colors.PRIMARY,
            scale=0.8
        )
        self.layout.update()

    def reset(self):
        self.layout.data = False
        self.layout.content.content = ft.Icon(
            name=ft.Icons.PLAY_CIRCLE_OUTLINE,
            color=ft.Colors.PRIMARY,
            scale=0.8
        )
        self.layout.update()
