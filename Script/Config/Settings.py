import yaml
import flet as ft
from pathlib import Path


class AppConfig:
    def __init__(self):
        self.ROOT = self.root()
        self.CONFIG = self.config()
        self.FONT_PATH = self.ROOT / 'Asset' / 'Font'
        self.RESC_PATH = self.ROOT / 'Asset' / 'Resc'
        self.VIDEO_PATH = self.ROOT / 'Asset' / 'Video'
        self.THEME_PATH = self.ROOT / 'Asset' / 'Theme'
        self.DEVICE_PATH = self.ROOT / 'Asset' / 'Device'
        self.DATABASE_PATH = self.ROOT / 'Asset' / 'Database'
        self.PLUGIN_PATH = self.ROOT / 'Plugin'
        self.INFO = self.init_info()
        self.FONT = self.init_font()
        self.RESC = self.init_resc()
        self.VIDEO = self.init_video()
        self.APPEARANCE = self.init_appearance()
        self.DATABASE = self.init_database()
        self.PLUGIN = self.init_plugin()
        self.FIXED_COLORS = self.init_fixed_colors()
        self.FIXED_STYLES = self.init_fixed_styles()

    @staticmethod
    def root():
        return Path(__file__).parents[2]

    def config(self) -> dict:
        path = self.ROOT / 'Config' / 'config.yml'
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except FileNotFoundError:
            raise FileNotFoundError(f'No Such file: {path}')

    def edit_config(self, edit_data):
        path = self.ROOT / 'Config' / 'config.yml'
        try:
            with open(path, 'w', encoding='utf-8-sig') as f:
                yaml.dump(edit_data, f)
        except FileNotFoundError:
            raise FileNotFoundError(f'No Such file: {path}')

    @staticmethod
    def modulized_config(resc_path, config_path) -> dict:
        path = resc_path / config_path['list'][config_path['current']]
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except FileNotFoundError:
            raise FileNotFoundError(f'No Such file: {path}')

    def read_resc(self, resc):
        path = self.RESC_PATH / f'{resc}'
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except FileNotFoundError:
            raise FileNotFoundError(f'No Such file: {path}')

    def init_config(self):
        self.ROOT = self.root()
        self.CONFIG = self.config()
        self.FONT_PATH = self.ROOT / 'Asset' / 'Font'
        self.RESC_PATH = self.ROOT / 'Asset' / 'Resc'
        self.VIDEO_PATH = self.ROOT / 'Asset' / 'Video'
        self.THEME_PATH = self.ROOT / 'Asset' / 'Theme'
        self.DEVICE_PATH = self.ROOT / 'Asset' / 'Device'
        self.DATABASE_PATH = self.ROOT / 'Asset' / 'Database'
        self.PLUGIN_PATH = self.ROOT / 'Plugin'
        self.INFO = self.init_info()
        self.FONT = self.init_font()
        self.RESC = self.init_resc()
        self.VIDEO = self.init_video()
        self.APPEARANCE = self.init_appearance()
        self.DATABASE = self.init_database()
        self.PLUGIN = self.init_plugin()
        self.FIXED_COLORS = self.init_fixed_colors()
        self.FIXED_STYLES = self.init_fixed_styles()

    def reload(self):
        self.init_config()

    def reload_appearance(self):
        self.APPEARANCE = self.init_appearance()

    def reload_plugin(self):
        self.PLUGIN = self.init_plugin()

    def init_info(self) -> dict:
        info = self.CONFIG['info']
        return {
            'title': str(info['title']),
            'version': str(info['version']),
            'author': str(info['author']),
        }

    def init_font(self) -> dict:
        font = self.CONFIG['font']
        return {
            'path': {
                'headline': str(self.FONT_PATH / font['list'][font['current']['headline']]),
                'body': str(self.FONT_PATH / font['list'][font['current']['body']]),
                'label': str(self.FONT_PATH / font['list'][font['current']['label']]),
            },
            'family': {
                'headline': str(font['list'][font['current']['headline']]).removesuffix('.ttf'),
                'body': str(font['list'][font['current']['body']]).removesuffix('.ttf'),
                'label': str(font['list'][font['current']['label']]).removesuffix('.ttf'),
            },
            'size': {
                'large': int(font['size']['large']),
                'medium': int(font['size']['medium']),
                'small': int(font['size']['small']),
            }
        }

    def init_resc(self) -> dict:
        return {
            'op': self.read_resc('operation.yml'),
            'text': self.read_resc('text.yml'),
        }

    def init_video(self) -> dict:
        video = self.CONFIG['video']
        return {
            'intro': {
                'path': str(self.VIDEO_PATH / video['intro']['file']),
                'skip': bool(video['intro']['skip']),
            },
        }

    def init_appearance(self) -> dict:
        theme_mode = [ft.ThemeMode.LIGHT, ft.ThemeMode.DARK]
        theme_config = self.modulized_config(self.THEME_PATH, self.CONFIG['theme'])
        # headline > body > label
        text_themes = [[
            ft.TextStyle(
                font_family=family,
                size=self.FONT['size'][size],
                color=theme_config['color']['primary'],
            )
            for size in ['large', 'medium', 'small']]
            for family in ['headline', 'body', 'label']]

        return {
            'mode': theme_mode[self.CONFIG['theme']['mode']],
            'list': self.CONFIG['theme']['list'],
            'current': self.CONFIG['theme']['current'],
            'name': theme_config['name'],
            'theme': ft.Theme(
                color_scheme=ft.ColorScheme(
                    primary=theme_config['color']['primary'],
                    on_primary=theme_config['color']['on_primary'],
                    on_primary_fixed=theme_config['color']['on_primary_fixed'],
                    on_primary_container=theme_config['color']['on_primary_container'],

                    secondary=theme_config['color']['secondary'],
                    on_secondary=theme_config['color']['on_secondary'],
                    on_secondary_fixed=theme_config['color']['on_secondary_fixed'],
                    on_secondary_container=theme_config['color']['on_secondary_container'],

                    surface=theme_config['color']['surface'],
                    on_surface=theme_config['color']['on_surface'],
                ),
                text_theme=ft.TextTheme(
                    headline_large=text_themes[0][0],
                    headline_medium=text_themes[0][1],
                    headline_small=text_themes[0][2],
                    body_large=text_themes[1][0],
                    body_medium=text_themes[1][1],
                    body_small=text_themes[1][2],
                    label_large=text_themes[2][0],
                    label_medium=text_themes[2][1],
                    label_small=text_themes[2][2],
                ),

                tabs_theme=ft.TabsTheme(
                    label_text_style=text_themes[0][0],
                    unselected_label_text_style=text_themes[0][0],
                    divider_color=theme_config['color']['primary'],
                    label_color=theme_config['color']['on_primary'],
                    indicator_color=theme_config['color']['on_primary'],
                    indicator_border_radius=ft.BorderRadius(1, 1, 1, 1),
                ),
                snackbar_theme=ft.SnackBarTheme(
                    bgcolor=theme_config['color']['primary'],
                    content_text_style=ft.TextStyle(
                        font_family='body',
                        size=self.FONT['size']['large'],
                        color=ft.Colors.SURFACE,
                    ),
                    alignment=ft.alignment.center,
                    shape=ft.RoundedRectangleBorder(radius=5),
                    behavior=ft.SnackBarBehavior.FIXED,
                ),
                divider_theme=ft.DividerTheme(
                    color=theme_config['color']['primary'],
                ),
                icon_theme=ft.IconTheme(
                    color=ft.Colors.SURFACE,
                ),
                scrollbar_theme=ft.ScrollbarTheme(
                    thumb_color=theme_config['color']['primary'],
                    cross_axis_margin=-5,
                    radius=3,
                )
            )
        }

    def init_database(self) -> dict:
        return {
            'log': self.DATABASE_PATH / 'Log.db'
        }

    def get_plugin_files(self, plugin_dict: str) -> list:
        return [f.name for f in Path(self.PLUGIN_PATH / plugin_dict).glob('*.py')
                if f.name != '__init__.py']

    def init_plugin(self) -> dict:
        return {
            'hid': self.get_plugin_files('HID'),
            'device': self.get_plugin_files('Device')
        }

    @staticmethod
    def init_fixed_colors() -> dict:
        return {
            'warning': ft.Colors.YELLOW_800,
            'error': ft.Colors.RED_800,
            'sub_content': ft.Colors.with_opacity(0.8, ft.Colors.GREY_800),
        }

    def init_fixed_styles(self) -> dict:
        return {
            'table_tab': ft.TextStyle(
                font_family='body',
                size=self.FONT['size']['medium'],
            ),
            'hint_text': ft.TextStyle(
                font_family='headline',
                size=self.FONT['size']['medium'],
                color=ft.Colors.with_opacity(0.8, ft.Colors.GREY_800),
            ),
            'list_button': ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=0)
            ),
            'icon_button': ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5),
                color=ft.Colors.SURFACE,
                bgcolor=ft.Colors.PRIMARY,
                overlay_color=ft.Colors.ON_PRIMARY
            ),
        }

    def read_hidmap(self):
        path = self.RESC_PATH / 'hidmap' / 'code.yml'
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def read_keymap(self, language):
        path = self.RESC_PATH / 'keymap' / f'{language}.yml'
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    # def read_hid_plugin(self, hid):
    #     path = self.PLUGIN_PATH / 'HID' / hid
    #     lines = []
    #     with open(path, 'r', encoding='utf-8') as f:
    #         for line in f:
    #             lines.append(line.rstrip())
    #     return lines

    def read_plugin(self, dict_name, file_name):
        path = self.PLUGIN_PATH / dict_name / file_name
        lines = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                lines.append(line.rstrip())
        return lines

    def get_language_list(self):
        path = self.RESC_PATH / 'keymap'
        return [f.stem for f in path.glob("*.yml")]

    def add_theme_style(self, file_name):
        config = self.CONFIG
        if file_name not in config['theme']['list']:
            config['theme']['list'].append(file_name)
        self.edit_config(config)
        self.CONFIG = config
        self.reload_appearance()

    def remove_theme_style(self, index):
        config = self.CONFIG
        removed_theme = config['theme']['list'][index]
        if removed_theme in config['theme']['list']:
            config['theme']['list'].remove(removed_theme)
        self.edit_config(config)
        self.CONFIG = config
        return removed_theme
