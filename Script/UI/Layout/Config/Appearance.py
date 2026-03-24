import flet as ft
from pathlib import Path
from Script.Abstracts import AbstractUI

THEME_MODES = ['Light', 'Dark']
VIDEO_MODES = ['Play', 'Skip']
FONT_SIZES = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
CONFIGS_ITEMS = {
    'Theme': ['Mode', 'Style'],
    'Font': ['Headline', 'Body', 'Label'],
    'Video': ['Intro'],
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
                    self.control.appearance_bodies[0],
                    self.control.theme_mode_config,
                    self.control.theme_style_config,
                    self.control.appearance_divider,
                    self.control.appearance_bodies[1],
                    self.control.font_config,
                    self.control.appearance_divider,
                    self.control.appearance_bodies[2],
                    self.control.intro_video_config,
                ],
                alignment=ft.alignment.top_left,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            expand=True
        )

    def reset_app_theme_mode(self):
        self.config.CONFIG['theme']['mode'] = self.control.theme_mode_button.selected_index
        self.config.edit_config(self.config.CONFIG)
        self.config.reload()
        self.control.reset_theme_mode()
        self.page.update()

    def reset_app_theme_style(self, index: int):
        self.config.CONFIG['theme']['current'] = index
        self.config.edit_config(self.config.CONFIG)
        self.config.reload()
        self.control.reset_theme_style()
        self.page.update()

    def reset_intro_skip_config(self):
        skip = self.control.intro_skip_button.selected_index
        self.config.CONFIG['video']['intro']['skip'] = False if skip == 0 else True
        self.config.edit_config(self.config.CONFIG)
        self.config.reload()
        self.page.update()

    def reset_app_font_size(self, type_index: int, size_index: int):
        size_keys = list(self.config.CONFIG['font']['size'])
        self.config.CONFIG['font']['size'][size_keys[type_index]] = FONT_SIZES[size_index]
        self.config.edit_config(self.config.CONFIG)
        self.config.reload()
        self.control.reset_font_size(type_index, size_index)
        self.page.update()

    def reset_app_font_family(self, type_index: int, family_index: int):
        type_key = CONFIGS_ITEMS['Font'][type_index].lower()
        self.config.CONFIG['font']['current'][type_key] = family_index
        self.config.edit_config(self.config.CONFIG)
        self.config.reload()
        self.control.reset_font_family(type_index, family_index)
        self.page.update()

    def add_theme_style_file(self, e):
        self.file_op.import_yaml_file(e, callback=self.control.update_theme_style_option)

    def delete_app_theme_confirm(self, e, index):
        dialog = ft.AlertDialog(
            modal=True,
            content=ft.Text(f"{self.config.RESC['text']['delete']['content']} theme: "
                            f"'{Path(self.config.APPEARANCE['list'][index]).stem}' ?"),
            actions=[
                ft.TextButton(f"{self.config.RESC['text']['cancel']}",
                              on_click=lambda e: self.page.close(dialog)),
                ft.TextButton(f"{self.config.RESC['text']['confirm']}",
                              on_click=lambda e: self.delete_app_theme(e, index, dialog))
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        self.page.open(dialog)

    def delete_app_theme(self, e, index, dialog):
        file_name = self.config.remove_theme_style(index)
        self.file_op.delete_theme_file(file_name)
        self.control.update_theme_style_option()
        self.page.close(dialog)


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
        self.current_config_names = self.init_current_config_names()
        self.appearance_bodies = self.init_appearance_bodies()
        self.appearance_divider = self.init_appearance_divider()
        self.appearance_labels = self.init_appearance_labels()
        # theme config
        self.theme_style_option_buttons = self.init_theme_style_option_buttons()
        self.theme_style_options = self.init_theme_style_options()
        self.theme_style_button = self.init_theme_style_button()
        self.theme_style_config = self.init_theme_style_config()
        self.theme_mode_button = self.init_theme_mode_button()
        self.theme_mode_config = self.init_theme_mode_config()
        # font config
        self.font_size_buttons = self.init_font_size_buttons()
        self.font_family_buttons = self.init_font_family_buttons()
        self.font_config = self.init_font_config()
        # intro config
        self.intro_skip_button = self.init_intro_skip_button()
        self.intro_video_config = self.init_intro_video_config()

    def init_current_config_names(self):
        return {
            'theme': [
                ft.Text(
                    value=self.data_ft.truncate_text(str(name), 20),
                    style=ft.TextThemeStyle.BODY_SMALL,
                )
                for name in [
                    self.config.APPEARANCE['name'],
                    THEME_MODES[self.config.CONFIG['theme']['mode']]
                ]
            ],
            'font': {
                'size': [
                    ft.Text(
                        value=self.data_ft.truncate_text(str(size), 10),
                        style=ft.TextThemeStyle.BODY_SMALL,
                    )
                    for size in self.config.FONT['size'].values()
                ],
                'family': [
                    ft.Text(
                        value=self.data_ft.truncate_text(str(name), 10),
                        style=ft.TextThemeStyle.BODY_SMALL,
                    )
                    for name in self.config.FONT['family'].values()
                ],
            }
        }

    @staticmethod
    def init_appearance_bodies():
        return [
            ft.Text(
                value=label,
                style=ft.TextThemeStyle.BODY_MEDIUM,
                width=80,
                height=20,
            ) for label in CONFIGS_ITEMS.keys()
        ]

    @staticmethod
    def init_appearance_labels():
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

    @staticmethod
    def init_appearance_divider():
        return ft.Container(
            content=ft.Divider(
                height=10,
                thickness=1.5,
            ),
            width=300,
        )

    def init_theme_mode_button(self):
        selected_index = self.config.CONFIG['theme']['mode']
        return ft.CupertinoSlidingSegmentedButton(
            selected_index=selected_index,
            controls=[
                ft.Text(
                    value=mode,
                    theme_style=ft.TextThemeStyle.LABEL_SMALL
                ) for index, mode in enumerate(THEME_MODES)
            ],
            width=200,
            on_change=lambda e: self.panel.reset_app_theme_mode()
        )

    def init_theme_mode_config(self):
        return ft.Row(
            controls=[
                self.appearance_labels['Theme'][0],
                self.theme_mode_button,
            ]
        )

    def init_add_theme_style_btn(self):
        return ft.ElevatedButton(
            expand=False,
            content=ft.Text(
                value=self.config.RESC['text']['config']['ap']['style']['add'],
                theme_style=ft.TextThemeStyle.LABEL_SMALL
            ),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0)),
            width=200,
            height=40,
            on_click=lambda e: self.panel.add_theme_style_file(e)
        )

    def init_theme_style_option_buttons(self):
        add_theme_style_btn = self.init_add_theme_style_btn()
        controls = [
            ft.ElevatedButton(
                expand=False,
                content=ft.Text(
                    value=Path(item).stem if item else "unknown",
                    theme_style=ft.TextThemeStyle.LABEL_SMALL,
                ),
                width=200,
                height=40,
                style=self.config.FIXED_STYLES['list_button'],
                on_click=lambda e, idx=index: self.panel.reset_app_theme_style(idx),
                on_long_press=lambda e, idx=index: self.panel.delete_app_theme_confirm(e, idx)
            )
            for index, item in enumerate(self.config.APPEARANCE['list'] or [])
        ]
        controls.append(add_theme_style_btn)
        return controls

    def init_theme_style_options(self):
        return ft.Container(
            height=120,
            content=ft.Column(
                controls=self.theme_style_option_buttons,
                scroll=ft.ScrollMode.AUTO,
                spacing=0
            )
        )

    def update_theme_style_option(self):
        self.theme_style_option_buttons = self.init_theme_style_option_buttons()
        self.theme_style_options.content.controls = self.theme_style_option_buttons
        self.theme_style_options.update()

    def init_theme_style_button(self):
        return ft.MenuBar(
            expand=False,
            style=ft.MenuStyle(
                alignment=ft.alignment.center,
                mouse_cursor={
                    ft.ControlState.HOVERED: ft.MouseCursor.WAIT,
                    ft.ControlState.DEFAULT: ft.MouseCursor.ZOOM_OUT,
                }
            ),
            controls=[
                ft.SubmenuButton(
                    content=self.current_config_names['theme'][0],
                    controls=[self.theme_style_options],
                    width=200
                )
            ]
        )

    def init_theme_style_config(self):
        return ft.Row(
            controls=[
                self.appearance_labels['Theme'][1],
                self.theme_style_button,
            ]
        )

    def init_font_size_options(self, type_index: int):
        return ft.Container(
            height=200,
            content=ft.Column(
                controls=[
                    ft.MenuItemButton(
                        expand=False,
                        content=ft.Text(
                            value=str(size),
                            theme_style=ft.TextThemeStyle.LABEL_SMALL,
                            size=size,
                        ),
                        width=90,
                        height=40,
                        on_click=lambda e, size_index=index: self.panel.reset_app_font_size(type_index, size_index)
                    ) for index, size in enumerate(FONT_SIZES)
                ],
                scroll=ft.ScrollMode.AUTO
            )
        )

    def init_font_size_buttons(self):
        return [
            ft.MenuBar(
                expand=False,
                style=ft.MenuStyle(
                    alignment=ft.alignment.center,
                    mouse_cursor={
                        ft.ControlState.HOVERED: ft.MouseCursor.WAIT,
                        ft.ControlState.DEFAULT: ft.MouseCursor.ZOOM_OUT,
                    },
                ),
                controls=[
                    ft.SubmenuButton(
                        content=name,
                        controls=[self.init_font_size_options(index)],
                        width=90,
                    )
                ]
            ) for index, name in enumerate(self.current_config_names['font']['size'])
        ]

    def init_font_family_options(self, type_index: int):
        return ft.Container(
            height=200,
            content=ft.Column(
                controls=[
                    ft.MenuItemButton(
                        expand=False,
                        content=ft.Text(
                            value=str(name).removesuffix('.ttf'),
                            theme_style=ft.TextThemeStyle.LABEL_SMALL,
                        ),
                        width=90,
                        height=40,
                        on_click=lambda e, family_index=index: self.panel.reset_app_font_family(type_index,
                                                                                                family_index)
                    ) for index, name in enumerate(self.config.CONFIG['font']['list'])
                ],
                scroll=ft.ScrollMode.AUTO
            )
        )

    def init_font_family_buttons(self):
        return [
            ft.MenuBar(
                expand=False,
                style=ft.MenuStyle(
                    alignment=ft.alignment.center,
                    mouse_cursor={
                        ft.ControlState.HOVERED: ft.MouseCursor.WAIT,
                        ft.ControlState.DEFAULT: ft.MouseCursor.ZOOM_OUT,
                    },
                ),
                controls=[
                    ft.SubmenuButton(
                        content=name,
                        controls=[self.init_font_family_options(index)],
                        width=90,
                    )
                ]
            ) for index, name in enumerate(self.current_config_names['font']['family'])
        ]

    def init_font_config(self):
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self.appearance_labels['Font'][index],
                        self.font_size_buttons[index],
                        self.font_family_buttons[index]
                    ]
                ) for index, name in enumerate(CONFIGS_ITEMS['Font'])
            ]
        )

    def init_intro_skip_button(self):
        selected_index = 0 if not self.config.VIDEO['intro']['skip'] else 1
        return ft.CupertinoSlidingSegmentedButton(
            selected_index=selected_index,
            controls=[
                ft.Text(
                    value=mode,
                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                ) for index, mode in enumerate(VIDEO_MODES)
            ],
            width=200,
            on_change=lambda e: self.panel.reset_intro_skip_config()
        )

    def init_intro_video_config(self):
        return ft.Row(
            controls=[
                self.appearance_labels['Video'][0],
                self.intro_skip_button
            ]
        )

    def reset_theme_mode(self):
        self.current_config_names['theme'][1].value = THEME_MODES[self.config.CONFIG['theme']['mode']]
        self.page.theme_mode = self.config.APPEARANCE['mode']

    def reset_theme_style(self):
        self.current_config_names['theme'][0].value = self.config.APPEARANCE['name']
        self.page.theme = self.config.APPEARANCE['theme']

    def reset_font_size(self, type_index: int, size_index: int):
        self.current_config_names['font']['size'][type_index].value = self.data_ft.truncate_text(
            str(FONT_SIZES[size_index]), 10)
        self.page.theme = self.config.APPEARANCE['theme']

    def reset_font_family(self, type_index: int, family_index: int):
        type_key = CONFIGS_ITEMS['Font'][type_index].lower()
        self.current_config_names['font']['family'][type_index].value = '*' + self.data_ft.truncate_text(
            str(self.config.FONT['family'][type_key]), 9)
        self.reset_font_family_hint()
        self.page.theme = self.config.APPEARANCE['theme']

    def reset_font_family_hint(self):
        self.page.open(
            ft.SnackBar(
                content=ft.Text(
                    value=self.config.RESC['text']['hint']['restart']['config'],
                    text_align=ft.TextAlign.CENTER,
                    expand=False
                ),
                duration=2000,
            )
        )
