from Script.UI.Layout import AppLayout
from Script import File, Globals


class Entity:
    def __init__(self, page, config, data_ft, db_op):
        self.globals = Globals.AppRegistry
        self.config = config
        self.page = page
        self.globals.register('page', self.page)
        self.file_op = File.File(self.page, self.config, data_ft, db_op)
        self.globals.register('file_op', self.file_op)

        self.main_layout = AppLayout.Panel()
        self.main_control = AppLayout.Control(self.main_layout)
        self.intro = self.main_layout.intro
        self.workbench = self.main_layout.workbench

    def init(self):
        self.page.window.icon = self.config.ICON['app']
        self.page.title = self.config.INFO['header']
        self.page.fonts = self.config.FONT['path']
        self.page.theme = self.config.APPEARANCE['theme']
        self.page.theme_mode = self.config.APPEARANCE['mode']
        self.page.window.resizable = True
        self.page.window.width = self.page.window.width
        self.page.window.height = self.page.window.height
        self.page.add(self.main_layout.layout)
