import flet as ft
import flet_video as fv
import Config.PATH as confp
import Config.STYLE as confs


INTRO_VIDEO = fv.Video(
    playlist=[fv.VideoMedia(confp.VIDEO["intro"])],
    expand=True,
    autoplay=True,
    show_controls=False,
)

SKIP_BUTTON = ft.ElevatedButton(
    text="SKIP",
    style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=15),
        text_style=ft.TextStyle(
            font_family="moon_house",
            size=20,
        )
    ),
    on_click=None,
    bgcolor=confs.DEFAULT_DARK["button_color"],
    color=confs.DEFAULT_DARK["main_color_light"],
    width=100,
    height=50,
)

INTRO_LAYOUT = ft.Stack(
    controls=[
        INTRO_VIDEO,
        ft.Container(
            content=SKIP_BUTTON,
            top=20,
            right=20,
        ),
    ],
    expand=True,
)
