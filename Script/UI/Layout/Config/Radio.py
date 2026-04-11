import flet as ft
from Script.Abstracts import AbstractUI

CONFIG_ITEMS = {
    'Mousejack': ['Mode', 'Delay', 'Language'],
    'Replay': ['Mode', 'Delay', 'Frequency'],
    'Scan': ['Channels', 'Dwell', 'Ping', 'Timeout'],
    'Driver': ['Generic', 'RF', 'LNA']
}


class Panel(AbstractUI):
    instance = None
    config_layout = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__()
        if self.config_layout is None:
            self.control = Control(self)
        if self.config_layout is None:
            self.config_layout = self.init_config_layout()
        self.layout = self.init_layout()

    def init_config_layout(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    self.control.radio_bodies[0],
                    self.control.mj_mode_config,
                    self.control.mj_delay_config,
                    self.control.mj_parse_lang_config,
                    self.control.radio_divider,
                    self.control.radio_bodies[1],
                    self.control.rp_mode_config,
                    self.control.rp_delay_config,
                    self.control.rp_freq_config,
                    self.control.radio_divider,
                    self.control.radio_bodies[2],
                    self.control.sc_channels_config,
                    self.control.sc_dwell_config,
                    self.control.sc_ping_config,
                    self.control.sc_timeout_config,
                    self.control.radio_divider,
                    self.control.radio_bodies[3],
                    self.control.dv_generic_config,
                    self.control.dv_rf_config,
                    self.control.dv_lna_config
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            expand=True
        )

    def init_layout(self):
        return ft.Stack(
            controls=[
                self.config_layout,
                self.control.radio_save_button
            ],
            visible=False,
            expand=True
        )

    def set_parse_lang(self, e, lang):
        self.control.mj_parse_lang_button.content.value = str(lang).upper()
        self.control.mj_parse_lang_button.data = str(lang).lower()
        self.control.mj_parse_lang_button.update()

    def save_radio_config(self, e):
        result = self.data_ft.update_radio_config_dict(
            self.control.current_radio_data,
            int(self.control.mj_mode_button.selected_index),
            str(self.control.mj_parse_lang_button.data).lower(),
            float(self.control.mj_delay_window.value),
            int(self.control.rp_mode_button.selected_index),
            float(self.control.rp_delay_window.value),
            int(self.control.rp_freq_window.value),
            int(self.control.sc_channels_from_window.value),
            int(self.control.sc_channels_to_window.value),
            float(self.control.sc_dwell_window.value),
            str(self.control.sc_ping_window.value),
            float(self.control.sc_timeout_window.value),
            bool(self.control.dv_generic_button.selected_index == 0),
            int(self.control.dv_rf_button.selected_index),
            bool(self.control.dv_lna_button.selected_index == 0)
        )
        self.config.RADIO_CONFIG_CACHE = result[1]
        update_text = f"{self.config.RESC['text']['radio']['update']} "
        self.page.open(
            ft.SnackBar(
                content=ft.Text(
                    value=update_text + 'Successfully' if
                    result[0] else update_text + 'Ignored Error',
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=ft.Colors.PRIMARY if result[0] else self.config.FIXED_COLORS['warning'],
                duration=2000,
            )
        )

    def on_ping_change(self, e):
        value = e.control.value
        if value and not self.data_ft.is_valid_ping_partial(value):
            e.control.border_color = ft.Colors.ERROR
        else:
            e.control.border_color = ft.Colors.PRIMARY
        e.control.update()


class Control(AbstractUI):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
        self.radio_config_dict = list(CONFIG_ITEMS.keys())
        self.radio_divider = self.init_radio_divider()
        self.radio_bodies = self.init_radio_bodies()
        self.radio_labels = self.init_radio_labels()
        #Mousejack
        self.mj_mode_button = self.init_atk_mode_button('mj')
        self.mj_mode_config = self.init_config('Mousejack', 0, self.mj_mode_button)
        self.mj_delay_window = self.init_atk_delay_window('mj')
        self.mj_delay_config = self.init_config('Mousejack', 1, self.mj_delay_window)
        self.mj_parse_lang_button = self.init_parse_lang_button()
        self.mj_parse_lang_config = self.init_config('Mousejack', 2, self.mj_parse_lang_button)
        #Replay
        self.rp_mode_button = self.init_atk_mode_button('rp')
        self.rp_mode_config = self.init_config('Replay', 0, self.rp_mode_button)
        self.rp_delay_window = self.init_atk_delay_window('rp')
        self.rp_delay_config = self.init_config('Replay', 1, self.rp_delay_window)
        self.rp_freq_window = self.init_atk_freq_window('rp')
        self.rp_freq_config = self.init_config('Replay', 2, self.rp_freq_window)
        #Scan
        self.sc_channels_from_window = self.init_sc_channel_range_window('from')
        self.sc_channels_to_window = self.init_sc_channel_range_window('to')
        self.sc_channels_windows = self.init_sc_channels_windows()
        self.sc_channels_config = self.init_config('Scan', 0, self.sc_channels_windows)
        self.sc_dwell_window = self.init_sc_time_window('dwell')
        self.sc_dwell_config = self.init_config('Scan', 1, self.sc_dwell_window)
        self.sc_ping_window = self.init_sc_ping_window()
        self.sc_ping_config = self.init_config('Scan', 2, self.sc_ping_window)
        self.sc_timeout_window = self.init_sc_time_window('timeout')
        self.sc_timeout_config = self.init_config('Scan', 3, self.sc_timeout_window)
        #Driver
        self.dv_generic_button = self.init_dv_mode_button('generic')
        self.dv_generic_config = self.init_config('Driver', 0, self.dv_generic_button)
        self.dv_rf_button = self.init_dv_rf_button()
        self.dv_rf_config = self.init_config('Driver', 1, self.dv_rf_button)
        self.dv_lna_button = self.init_dv_mode_button('lna')
        self.dv_lna_config = self.init_config('Driver', 2, self.dv_lna_button)
        #Save
        self.current_radio_data = self.init_current_radio_data()
        self.radio_save_button = self.init_radio_save_button()

    @staticmethod
    def init_radio_divider():
        return ft.Container(
            content=ft.Divider(
                height=10,
                thickness=1.5,
            ),
            expand=True
        )

    @staticmethod
    def init_radio_bodies():
        return [
            ft.Text(
                value=label,
                style=ft.TextThemeStyle.BODY_MEDIUM,
                width=80,
                height=20,
            ) for label in CONFIG_ITEMS.keys()
        ]

    @staticmethod
    def init_radio_labels():
        return {
            category: [
                ft.Text(
                    value=item,
                    style=ft.TextThemeStyle.LABEL_SMALL,
                    width=80,
                )
                for item in items
            ]
            for category, items in CONFIG_ITEMS.items()
        }

    def init_atk_mode_button(self, key):
        selected_index = self.config.RESC['rd'][key]['mode_index']
        modes = self.config.RESC['rd'][key]['modes']
        return ft.CupertinoSlidingSegmentedButton(
            selected_index=selected_index,
            controls=[
                ft.Text(
                    value=mode,
                    theme_style=ft.TextThemeStyle.LABEL_SMALL
                ) for index, mode in enumerate(modes)
            ],
            width=200
        )

    def init_config(self, label, index, control):
        return ft.Row(
            controls=[
                self.radio_labels[label][index],
                control
            ],
            height=40
        )

    def init_atk_delay_window(self, key):
        return ft.TextField(
            input_filter=ft.InputFilter(
                allow=True,
                regex_string=r"^[0-9.]*$",
            ),
            value=self.config.RESC['rd'][key]['delay'],
            suffix_text='s',
            text_style=self.config.FIXED_STYLES['config_text'],
            text_align=ft.TextAlign.CENTER,
            suffix_style=self.config.FIXED_STYLES['config_text'],
            border_color=ft.Colors.PRIMARY,
            focused_border_color=ft.Colors.ON_PRIMARY,
            width=200
        )

    def init_atk_freq_window(self, key):
        return ft.TextField(
            input_filter=ft.InputFilter(
                allow=True,
                regex_string=r"^[0-9]*$",
            ),
            value=self.config.RESC['rd'][key]['freq'],
            suffix_text='Hz',
            text_style=self.config.FIXED_STYLES['config_text'],
            text_align=ft.TextAlign.CENTER,
            suffix_style=self.config.FIXED_STYLES['config_text'],
            border_color=ft.Colors.PRIMARY,
            focused_border_color=ft.Colors.ON_PRIMARY,
            width=200
        )

    def init_parse_lang_button(self):
        def lang_btn(text, handler):
            return ft.MenuItemButton(
                content=ft.Text(
                    value=text,
                    theme_style=ft.TextThemeStyle.LABEL_SMALL,
                    text_align=ft.TextAlign.CENTER
                ),
                on_click=handler,
                width=200
            )

        language = self.config.RESC['rd']['mj']['language']
        return ft.SubmenuButton(
            data=str(language).lower(),
            content=ft.Text(
                value=str(language).upper(),
                theme_style=ft.TextThemeStyle.LABEL_SMALL,
                text_align=ft.TextAlign.CENTER,
                color=ft.Colors.SURFACE
            ),
            controls=[
                lang_btn(str(name).upper(),
                         lambda e, lang=name.lower():
                         self.panel.set_parse_lang(e, lang))
                for name in self.config.get_language_list()
            ],
            style=self.config.FIXED_STYLES['invert_color_button'],
            width=200
        )

    def init_sc_channel_range_window(self, key):
        return ft.TextField(
            input_filter=ft.InputFilter(
                allow=True,
                regex_string=r"^[0-9]*$",
            ),
            max_length=3,
            value=self.config.RESC['rd']['sc']['channels'][key],
            prefix_text=f'{key.upper().capitalize()} :',
            text_style=self.config.FIXED_STYLES['config_text'],
            text_align=ft.TextAlign.CENTER,
            prefix_style=self.config.FIXED_STYLES['config_text'],
            border_color=ft.Colors.PRIMARY,
            focused_border_color=ft.Colors.ON_PRIMARY,
            width=95
        )

    def init_sc_channels_windows(self):
        return ft.Row(
            controls=[self.sc_channels_from_window,
                      self.sc_channels_to_window]
        )

    def init_sc_time_window(self, key):
        return ft.TextField(
            input_filter=ft.InputFilter(
                allow=True,
                regex_string=r"^[0-9.]*$",
            ),
            value=self.config.RESC['rd']['sc'][key],
            suffix_text='s',
            text_style=self.config.FIXED_STYLES['config_text'],
            text_align=ft.TextAlign.CENTER,
            suffix_style=self.config.FIXED_STYLES['config_text'],
            border_color=ft.Colors.PRIMARY,
            focused_border_color=ft.Colors.ON_PRIMARY,
            width=200
        )

    def init_sc_ping_window(self):
        return ft.TextField(
            input_filter=ft.InputFilter(
                allow=True,
                regex_string=r"^[0-9a-fA-F,x]*$",
            ),
            value=self.config.RESC['rd']['sc']['ping'],
            text_style=self.config.FIXED_STYLES['config_text'],
            text_align=ft.TextAlign.START,
            border_color=ft.Colors.PRIMARY,
            focused_border_color=ft.Colors.ON_PRIMARY,
            on_change=lambda e: self.panel.on_ping_change(e),
            width=200
        )

    def init_dv_mode_button(self, key):
        if self.config.RESC['rd']['dv'][key]:
            selected_index = 0
        else:
            selected_index = 1
        return ft.CupertinoSlidingSegmentedButton(
            selected_index=selected_index,
            controls=[
                ft.Text(
                    value=mode,
                    theme_style=ft.TextThemeStyle.LABEL_SMALL
                ) for mode in ['Enable', 'Disable']
            ],
            width=200
        )

    def init_dv_rf_button(self):
        selected_index = self.config.RESC['rd']['dv']['rf_index']
        frequency = self.config.RESC['rd']['dv']['rf']
        return ft.CupertinoSlidingSegmentedButton(
            selected_index=selected_index,
            controls=[
                ft.Text(
                    value=rf,
                    theme_style=ft.TextThemeStyle.LABEL_SMALL
                ) for rf in frequency
            ],
            width=200
        )

    def init_current_radio_data(self):
        return self.config.RADIO_CONFIG_CACHE

    def init_radio_save_button(self):
        return ft.Container(ft.ElevatedButton(
            text=self.config.RESC['text']['save'],
            style=self.config.FIXED_STYLES['invert_color_button'],
            width=200,
            height=50,
            on_click=lambda e: self.panel.save_radio_config(e)
        ),
            expand=False,
            right=5,
            top=0,
        )
