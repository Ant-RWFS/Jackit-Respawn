import flet as ft
from Frontend.Script import UI


def main(page: ft.Page):
    ui = UI.Entity(page)
    ui.init()
    ui.play_intro_video()


ft.app(target=main)

