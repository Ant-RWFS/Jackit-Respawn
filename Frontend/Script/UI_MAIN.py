import flet as ft
from . import UI_FUNC as uif
from . import UI_INTRO as uii


MAIN_LAYOUT = ft.Stack(
    controls=[
        uif.FUNCTION_LAYOUT,
        uii.INTRO_LAYOUT,
    ],
    expand=True,
)
