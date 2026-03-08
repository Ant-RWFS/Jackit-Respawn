import flet as ft
from Script.UI.Layout.Homepage import HomeBlock
from Script.UI.Layout.Log import LogBlock
from Script.UI.Layout.Config import ConfigBlock
from Script.Abstracts import AbstractUI

TABS = [
    {
        "text": "HOME",
        "icon": ft.Icons.CENTER_FOCUS_STRONG,
    },
    {
        "text": "LOG",
        "icon": ft.Icons.LIBRARY_BOOKS,
    },
    {
        "text": "CONF",
        "icon": ft.Icons.SETTINGS,
    }
]


class Panel(AbstractUI):
    def __init__(self):
        super().__init__()
        self.control = Control(self)
        self.layout = self.init_layout()

    def init_layout(self):
        return ft.Column(
            controls=[
                self.control.switch_bar,
                self.control.blocks
            ]
        )

    def switch_page(self, e):
        self.show_block(e.control.selected_index)

    def show_block(self, index):
        self.hide_blocks()
        self.control.blocks.controls[index].visible = True
        self.control.blocks.controls[index].update()

    def hide_blocks(self):
        for block in self.control.blocks.controls:
            block.visible = False
            block.update()


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
        self.switch_bar = self.init_switch_bar()

        self.home_block = HomeBlock.Panel()
        self.log_block = LogBlock.Panel()
        self.conf_block = ConfigBlock.Panel()

        self.home_panel = self.home_block.layout
        self.log_panel = self.log_block.layout
        self.conf_panel = self.conf_block.layout

        self.blocks = self.init_blocks()

    def init_switch_bar(self):
        return ft.Tabs(
            tabs=[
                ft.Tab(
                    tab_content=ft.Row(
                        width=100,
                        alignment=ft.alignment.top_left,
                        controls=[
                            ft.Icon(tab["icon"]),
                            ft.Text(tab["text"]),
                        ]
                    ),
                )
                for tab in TABS
            ],
            scrollable=True,
            selected_index=0,
            animation_duration=150,
            on_change=self.panel.switch_page,
            tab_alignment=ft.TabAlignment.START,
            expand=False,
        )

    def init_blocks(self):
        return ft.Stack(
            controls=[
                self.home_panel,
                self.log_panel,
                self.conf_panel,
            ],
            expand=True
        )
