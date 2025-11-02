import time
from . import UI_MAIN as uim
from . import UI_FUNC as uif
from . import UI_INTRO as uii
import Config.INFO as confi
import Config.PATH as confp


class Entity:
    def __init__(self, page):
        self.page = page
        self.intro_start_time = None
        self.intro_elapsed_time = 0
        self.intro_running = False

    def init(self):
        self.page.title = confi.TITLE
        self.page.fonts = confp.FONT
        self.page.window.resizable = False
        self.page.window.width = self.page.window.width
        self.page.window.height = self.page.window.height
        self.page.add(uim.MAIN_LAYOUT)
        uii.SKIP_BUTTON.on_click = self.close_intro_video
        uif.FUNCTION_BAR.on_change = self.function_switch

    def play_intro_video(self):
        uif.FUNCTION_LAYOUT.visible = False
        uii.INTRO_LAYOUT.visible = True
        self.start_intro(7.5)
        self.page.update()

    def close_intro_video(self, e):
        uif.FUNCTION_LAYOUT.visible = True
        uii.INTRO_LAYOUT.visible = False
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
            uif.FUNCTION_LAYOUT.visible = True
            uii.INTRO_LAYOUT.visible = False
            self.intro_elapsed_time = time.time() - self.intro_start_time
            self.intro_running = False

    def reset_intro(self):
        self.intro_start_time = None
        self.intro_elapsed_time = 0
        self.intro_running = False

    def function_switch(self, e):
        selected_index = e.control.selected_index

        if selected_index == 0:
            self.switch_home()
        elif selected_index == 1:
            self.switch_fpr()
        elif selected_index == 2:
            self.switch_log()
        elif selected_index == 3:
            self.switch_conf()

    def switch_home(self):
        uif.hide_blocks()
        uif.HOME_BLOCK.visible = True
        self.page.update()

    def switch_fpr(self):
        uif.hide_blocks()
        uif.FPR_BLOCK.visible = True
        self.page.update()

    def switch_log(self):
        uif.hide_blocks()
        uif.LOG_BLOCK.visible = True
        self.page.update()

    def switch_conf(self):
        uif.hide_blocks()
        uif.CONF_BLOCK.visible = True
        self.page.update()
