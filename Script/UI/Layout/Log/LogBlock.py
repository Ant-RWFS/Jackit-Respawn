import flet as ft
from Script.Abstracts import AbstractUI

TABS = [
    {
        'text': 'Scanned Info',
        'icon': ft.Icons.RADAR,
    },
    {
        'text': 'User Action',
        'icon': ft.Icons.PERSON,
    },
    {
        'text': 'System Event',
        'icon': ft.Icons.MEMORY,
    }
]


class Panel(AbstractUI):
    def __init__(self):
        super().__init__()
        self.control = Control(self)
        self.layout = self.init_layout()

    def init_layout(self):
        return ft.Row(
            controls=[
                self.control.log_panel,
            ],
            visible=False,
            expand=True
        )

    def switch_table(self, e):
        index = e.control.selected_index
        self.show_table(index)
        self.control.update_table_pages_count()
        self.control.display_table_data(index)

    def show_table(self, index):
        self.hide_tables()
        self.control.tables.controls[index].visible = True
        self.control.tables.controls[index].update()

    def hide_tables(self):
        for table in self.control.tables.controls:
            table.visible = False
            table.update()


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
        self.table_tab_bar = self.init_table_tab_bar()
        self.recv_data_table = self.init_recv_data_table()
        self.user_actions_table = self.init_user_actions_table()
        self.system_events_table = self.init_system_events_table()
        self.current_page_text = self.init_current_page_text()
        self.table_page_controller = self.init_table_page_controller()
        self.tables = self.init_tables()
        self.table_window = self.init_table_window()
        self.log_panel = self.init_log_panel()
        self.update_table_pages_count()

    def init_table_tab_bar(self):
        return ft.Tabs(
            tabs=[
                ft.Tab(
                    tab_content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Icon(tab['icon'], scale=0.8),
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    value=tab['text'],
                                    style=self.config.FIXED_STYLES['table_tab'],
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                alignment=ft.alignment.center,
                            )
                        ],
                        spacing=0,
                        width=150,
                    ),
                )
                for tab in TABS
            ],
            scrollable=True,
            selected_index=0,
            animation_duration=150,
            divider_color=ft.Colors.TRANSPARENT,
            on_change=lambda e: self.panel.switch_table(e),
            tab_alignment=ft.TabAlignment.CENTER,
            expand=False,
        )

    @staticmethod
    def init_recv_data_table():
        columns = [
            ft.DataColumn(label=ft.Text(name, theme_style=ft.TextThemeStyle.LABEL_SMALL))
            for name in ['No.', 'Timestamp', 'Address', 'Channels', 'HID', 'Data', 'Row Data', 'Detector']
        ]
        return ft.DataTable(
            columns=columns,
            rows=[],
            expand=True
        )

    @staticmethod
    def init_user_actions_table():
        columns = [
            ft.DataColumn(label=ft.Text(name, theme_style=ft.TextThemeStyle.LABEL_SMALL))
            for name in ['No.', 'Timestamp', 'Action', 'Payload', 'Target Address', 'Target Channels', 'Target HID']
        ]
        return ft.DataTable(
            columns=columns,
            rows=[],
            expand=True
        )

    @staticmethod
    def init_system_events_table():
        columns = [
            ft.DataColumn(label=ft.Text(name, theme_style=ft.TextThemeStyle.LABEL_SMALL))
            for name in ['No.', 'Timestamp', 'Event', 'Detail']
        ]
        return ft.DataTable(
            columns=columns,
            rows=[],
            expand=True
        )

    @staticmethod
    def init_current_page_text():
        return ft.Text(
            value='1',
            theme_style=ft.TextThemeStyle.LABEL_MEDIUM,
            width=50,
            text_align=ft.TextAlign.CENTER
        )

    def init_table_page_controller(self):
        first_page_btn = ft.IconButton(
            icon=ft.Icons.FIRST_PAGE,
            on_click=lambda e: self.display_first_page(e)
        )
        prev_btn = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            on_click=lambda e: self.display_previous_page(e)
        )
        next_btn = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            on_click=lambda e: self.display_next_page(e)
        )
        last_page_btn = ft.IconButton(
            icon=ft.Icons.LAST_PAGE,
            on_click=lambda e: self.display_last_page(e)
        )
        return ft.Row(
            controls=[
                first_page_btn,
                prev_btn,
                self.current_page_text,
                next_btn,
                last_page_btn
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

    def init_tables(self):
        return ft.Stack(
            controls=[
                ft.Row(
                    data={'page': 1, 'limit': 20, 'last': 1},
                    controls=[self.recv_data_table],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                    visible=True
                ),
                ft.Row(
                    data={'page': 1, 'limit': 20, 'last': 1},
                    controls=[self.user_actions_table],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                    visible=False
                ),
                ft.Row(
                    data={'page': 1, 'limit': 20, 'last': 1},
                    controls=[self.system_events_table],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                    visible=False
                )
            ],
            expand=True
        )

    def init_table_window(self):
        return ft.Container(
            content=ft.Column(
                controls=[self.tables],
                expand=True,
                scroll=ft.ScrollMode.ALWAYS
            ),
            border=ft.border.all(1, ft.Colors.PRIMARY),
            border_radius=5,
            expand=True
        )

    def init_log_panel(self):
        self.display_table_data(0)
        return ft.Column(
            controls=[
                self.table_tab_bar,
                self.table_window,
                self.table_page_controller
            ],
            expand=True
        )

    def display_first_page(self, e):
        index = self.table_tab_bar.selected_index
        self.tables.controls[index].data['page'] = 1
        self.display_table_data(index)

    def display_previous_page(self, e):
        index = self.table_tab_bar.selected_index
        table_page = self.tables.controls[index].data['page']
        if table_page > 1:
            self.tables.controls[index].data['page'] -= 1
        self.display_table_data(index)

    def display_next_page(self, e):
        index = self.table_tab_bar.selected_index
        table_page = self.tables.controls[index].data['page']
        if table_page < self.tables.controls[index].data['last']:
            self.tables.controls[index].data['page'] += 1
        self.display_table_data(index)

    def display_last_page(self, e):
        index = self.table_tab_bar.selected_index
        self.db_op.get_table_total_count_async(
            index=index,
            callback=lambda total: self.go_to_last_page(index, total)
        )

    def go_to_last_page(self, index, total):
        if total != 0:
            limit = self.tables.controls[index].data['limit']
            last_page = (total + limit - 1) // limit
            self.tables.controls[index].data['page'] = last_page
            self.display_table_data(index)

    def update_table_pages_count(self):
        index = self.table_tab_bar.selected_index
        self.db_op.get_table_total_count_async(
            index=index,
            callback=lambda total: self.set_table_page_count(index, total)
        )

    def set_table_page_count(self, index, total):
        if total != 0:
            limit = self.tables.controls[index].data['limit']
            last_page = (total + limit - 1) // limit
            self.tables.controls[index].data['last'] = last_page

    def display_table_data(self, index):
        table = None
        row = None
        if index == 0:
            table = self.recv_data_table
            row = self.recv_data_row
        elif index == 1:
            table = self.user_actions_table
            row = self.user_actions_row
        elif index == 2:
            table = self.system_events_table
            row = self.system_events_row
        if table and row:
            page = self.tables.controls[index].data['page']
            limit = self.tables.controls[index].data['limit']
            start_no = (page - 1) * limit + 1
            self.db_op.select_data_by_table_index(
                index=index,
                callback=lambda data_list: self.update_table_rows(data_list, table, row),
                start_no=start_no,
                limit=limit
            )

    def update_current_page(self):
        index = self.table_tab_bar.selected_index
        self.current_page_text.value = str(self.tables.controls[index].data['page'])
        self.current_page_text.update()

    def update_table_rows(self, data_list, table: ft.DataTable, row):
        rows = [row(data) for data in data_list]
        table.rows = rows
        table.update()
        self.update_current_page()

    def recv_data_row(self, data):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(data['no'])),
                ft.DataCell(ft.Text(data['timestamp'])),
                ft.DataCell(ft.Text(data['address'])),
                ft.DataCell(ft.Text(data['channels'])),
                ft.DataCell(ft.Text(data['hid'])),
                ft.DataCell(ft.Text(data['data'])),
                ft.DataCell(ft.Text(data['raw_data']),
                            on_tap=lambda e: self.copy_raw_data_to_clipboard(data['raw_data'])),
                ft.DataCell(ft.Text(data['detector'])),
            ],
            on_long_press=lambda e: self.copy_data_row_to_clipboard(data)
        )

    def user_actions_row(self, data):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(data['no'])),
                ft.DataCell(ft.Text(data['timestamp'])),
                ft.DataCell(ft.Text(data['action'])),
                ft.DataCell(ft.Text(data['payload']),
                            on_tap=lambda e: self.copy_data_cell_to_clipboard(data['payload'])),
                ft.DataCell(ft.Text(data['target_address'])),
                ft.DataCell(ft.Text(data['target_channels'])),
                ft.DataCell(ft.Text(data['target_hid']))
            ],
            on_long_press=lambda e: self.copy_data_row_to_clipboard(data)
        )

    def system_events_row(self, data):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(data['no'])),
                ft.DataCell(ft.Text(data['timestamp'])),
                ft.DataCell(ft.Text(data['event'])),
                ft.DataCell(ft.Text(data['detail']),
                            on_tap=lambda e: self.copy_data_cell_to_clipboard(data['detail'])),
            ],
            on_long_press=lambda e: self.copy_data_row_to_clipboard(data)
        )

    def copy_data_row_to_clipboard(self, data):
        json = self.data_ft.dict_to_json(data)
        self.page.set_clipboard(json)

    def copy_raw_data_to_clipboard(self, raw_data):
        json = self.data_ft.raw_data_to_json(raw_data)
        self.page.set_clipboard(json)

    def copy_data_cell_to_clipboard(self, cell):
        self.page.set_clipboard(cell)
