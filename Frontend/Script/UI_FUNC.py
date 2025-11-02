import flet as ft
import Config.STYLE as confs

FUNCTION_TABS = [
    {
        "text": "HOME",
        "icon": ft.Icons.CENTER_FOCUS_STRONG,
    },
    {
        "text": "FPR",
        "icon": ft.Icons.FINGERPRINT,
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

FUNCTION_TABS = [
    ft.Tab(
        text=TAB["text"],
        icon=TAB["icon"],
    )
    for TAB in FUNCTION_TABS
]

FUNCTION_BAR = ft.Tabs(
    tabs=FUNCTION_TABS,
    on_change=None,
    scrollable=True,
    selected_index=0,
    animation_duration=300,
    tab_alignment=ft.TabAlignment.START,
    divider_color=confs.DEFAULT_DARK["main_color"],
    indicator_color=confs.DEFAULT_DARK["main_color_light"],
    label_color=confs.DEFAULT_DARK["main_color_light"],
    unselected_label_color=confs.DEFAULT_DARK["main_color"],
    label_text_style=ft.TextStyle(
        font_family="moon_house"
    ),
    expand=False,
)

#MouseJack
HOME_BLOCK = ft.Column(
    controls=[
        ft.TextField(
        )
    ],
    visible=True,
    expand=True
)


#FingerPrint
FPR_BLOCK = ft.Column(
    controls=[
        ft.TextField(
        )
    ],
    visible=False,
    expand=True
)

#Log
LOG_BLOCK = ft.Column(
    controls=[

    ],
    visible=False,
    expand=True
)

#Configuration
CONF_BLOCK = ft.Column(
    controls=[

    ],
    visible=False,
    expand=True
)

FUNCTION_BLOCK = ft.Stack(
    controls=[
        HOME_BLOCK,
        FPR_BLOCK,
        LOG_BLOCK,
        CONF_BLOCK,
    ],
    expand=True
)

FUNCTION_LAYOUT = ft.Column(
    controls=[
        FUNCTION_BAR,
        FUNCTION_BLOCK,
    ],
    alignment=ft.alignment.center,
    expand=True
)


def hide_blocks():
    for block in FUNCTION_BLOCK.controls:
        block.visible = False
