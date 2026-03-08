import time
import flet as ft
from . import Workbench
from Script.Abstracts import AbstractUI


class Panel(AbstractUI):
    def __init__(self, workbench: Workbench):
        super().__init__()
        self.workbench = workbench
        self.control = Control(self)
        self.layout = self.init_layout()
        self.intro_start_time = None
        self.intro_elapsed_time = 0
        self.intro_running = False

    def init_layout(self):
        return ft.Stack(
            controls=[
                self.control.intro_video,
                ft.Container(
                    content=self.control.skip_button,
                    top=20,
                    right=20,
                ),
            ],
            expand=True,
        )

    def start(self):
        if self.config.VIDEO["intro"]["skip"]:
            self.workbench.layout.visible = True
            self.close_intro_video()
        else:
            self.workbench.layout.visible = False
            self.layout.visible = True
            self.start_intro(7.5)
            self.page.update()

    def close_intro_video(self, e=None):
        self.workbench.layout.visible = True
        self.layout.visible = False
        self.reset_intro()
        self.page.update()

    def start_intro(self, interval):
        if not self.intro_running:
            self.intro_start_time = time.time() - self.intro_elapsed_time
            self.intro_running = True
        time.sleep(interval)
        self.stop_intro()

    def stop_intro(self):
        if self.intro_running:
            self.workbench.layout.visible = True
            self.layout.visible = False
            self.intro_elapsed_time = time.time() - self.intro_start_time
            self.intro_running = False

    def reset_intro(self):
        self.intro_start_time = None
        self.intro_elapsed_time = 0
        self.intro_running = False


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
        self.intro_video = self.init_intro_video()
        self.skip_button = self.init_skip_button()

    def init_intro_video(self):
        return ft.Video(
            playlist=[ft.VideoMedia(self.config.VIDEO["intro"]['path'])],
            expand=True,
            autoplay=True,
            show_controls=False,
        )

    def init_skip_button(self):
        return ft.Button(
            content=ft.Text(
                value="SKIP",
                theme_style=ft.TextThemeStyle.HEADLINE_LARGE
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=15)
            ),
            on_click=self.panel.close_intro_video,
            width=100,
            height=50,
        )
