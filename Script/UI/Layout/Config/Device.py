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
            expand=True,
        # on_click = lambda e: print(self.config.DEVICE)
        )


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel

    @staticmethod
    def init_device_divider():
        return ft.Container(
            content=ft.Divider(
                height=10,
                thickness=1.5,
            ),
            width=300,
        )

    def init_layout(self):
        return ft.Container(
            on_click=lambda e: print(self.config.DEVICE)
        )

