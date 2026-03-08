import flet as ft
from Script.Abstracts import AbstractUI


class Panel(AbstractUI):
    def __init__(self):
        super().__init__()
        self.control = Control(self)
        self.layout = self.init_layout()

    def init_layout(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text('Test', visible=True)
                ],
                alignment=ft.alignment.top_left,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            visible=False,
            expand=True
        )


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
