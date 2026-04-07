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
        'icon': ft.Icons.EVENT_NOTE,
    }
]


class Panel(AbstractUI):
    def __init__(self):
        super().__init__()
        self.control = Control(self)
        self.layout = self.init_layout()
        self.update_table_pages_count()
        self.display_table_data(0)

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
        self.update_table_pages_count()
        self.display_table_data(index)

    def show_table(self, index):
        self.hide_tables()
        self.control.tables.controls[index].visible = True
        self.control.tables.controls[index].update()

    def hide_tables(self):
        for table in self.control.tables.controls:
            table.visible = False
            table.update()

    def copy_raw_data_to_clipboard(self, raw_data):
        json = self.data_ft.raw_data_to_json(raw_data)
        self.page.set_clipboard(json)

    def copy_data_cell_to_clipboard(self, cell):
        self.page.set_clipboard(cell)

    def display_first_page(self):
        index = self.control.table_tab_bar.selected_index
        self.control.tables.controls[index].data['page'] = 1
        self.display_table_data(index)

    def display_previous_page(self):
        index = self.control.table_tab_bar.selected_index
        table_page = self.control.tables.controls[index].data['page']
        if table_page > 1:
            self.control.tables.controls[index].data['page'] -= 1
        self.display_table_data(index)

    def display_next_page(self):
        index = self.control.table_tab_bar.selected_index
        table_page = self.control.tables.controls[index].data['page']
        self.update_table_pages_count()
        if table_page < self.control.tables.controls[index].data['last']:
            self.control.tables.controls[index].data['page'] += 1
        self.display_table_data(index)

    def display_last_page(self):
        index = self.control.table_tab_bar.selected_index
        self.update_table_pages_count()
        self.db_op.get_table_total_count_async(
            index=index,
            callback=lambda total: self.go_to_last_page(index, total)
        )

    def go_to_last_page(self, index, total):
        if total != 0:
            limit = self.control.tables.controls[index].data['limit']
            last_page = (total + limit - 1) // limit
            self.control.tables.controls[index].data['page'] = last_page
            self.display_table_data(index)

    def update_table_pages_count(self):
        index = self.control.table_tab_bar.selected_index
        self.db_op.get_table_total_count_async(
            index=index,
            callback=lambda total: self.set_table_page_count(index, total)
        )

    def set_table_page_count(self, index, total):
        self.control.total_row_counts[index] = total
        if total != 0:
            limit = self.control.tables.controls[index].data['limit']
            last_page = (total + limit - 1) // limit
            self.control.tables.controls[index].data['last'] = last_page

    def display_table_data(self, index):
        table = None
        row = None
        self.control.current_row_checkboxes.clear()
        if index == 0:
            table = self.control.recv_data_table
            row = self.control.recv_data_row
        elif index == 1:
            table = self.control.user_actions_table
            row = self.control.user_actions_row
        elif index == 2:
            table = self.control.system_events_table
            row = self.control.system_events_row
        if table and row:
            page = self.control.tables.controls[index].data['page']
            limit = self.control.tables.controls[index].data['limit']
            start_no = (page - 1) * limit + 1
            self.db_op.select_data_by_table_index(
                index=index,
                callback=lambda data_list: self.update_table_rows(data_list, table, row, index),
                start_no=start_no,
                limit=limit
            )

    def update_current_page(self):
        index = self.control.table_tab_bar.selected_index
        self.control.current_page_text.value = str(self.control.tables.controls[index].data['page'])
        self.control.current_page_text.update()

    def update_table_rows(self, data_list, table: ft.DataTable, row, index):
        rows = [row(data, index) for data in data_list]
        table.rows = rows
        table.update()
        self.update_current_page()

    def update_selected_row(self, no, index, checkbox: ft.Checkbox):
        if self.control.table_checkboxes[index].value:
            if checkbox.value:
                self.select_row(no, index)
            else:
                self.unselect_row(no, index)
                self.unselect_table(index)
                self.control.selected_row[index].clear()
        else:
            if checkbox.value:
                self.select_row(no, index)
                if self.control.selected_row_counts[index] == self.control.total_row_counts[index]:
                    self.select_table(index)
                    self.control.unselected_row[index].clear()
            else:
                self.unselect_row(no, index)

    def select_row(self, no, index):
        if no not in self.control.selected_row[index]:
            self.control.selected_row[index].add(no)
            self.control.unselected_row[index].discard(no)
            self.control.selected_row_counts[index] += 1

    def unselect_row(self, no, index):
        if no not in self.control.unselected_row[index]:
            self.control.unselected_row[index].add(no)
            self.control.selected_row[index].discard(no)
            self.control.selected_row_counts[index] -= 1

    def select_table(self, index):
        self.control.table_checkboxes[index].value = True
        self.control.table_checkboxes[index].update()

    def unselect_table(self, index):
        self.control.table_checkboxes[index].value = False
        self.control.table_checkboxes[index].update()

    def update_table_selection(self, index, checkbox: ft.Checkbox):
        if checkbox.value:
            self.select_table(index)
            self.control.selected_row_counts[index] = self.control.total_row_counts[index]
            for box in self.control.current_row_checkboxes:
                box.value = True
                box.update()
        else:
            self.unselect_table(index)
            self.control.selected_row_counts[index] = 0
            for box in self.control.current_row_checkboxes:
                box.value = False
                box.update()

    def delete_selected_rows(self, dialog):
        self.page.close(dialog)
        index = self.control.table_tab_bar.selected_index

        if self.control.table_checkboxes[index].value:
            self.db_op.delete_all_rows_async(
                index=index,
                callback=lambda success, error: self.on_delete_complete(index, success, error)
            )

        elif self.control.selected_row_counts[index] != 0:
            if (len(self.control.unselected_row[index]) + self.control.selected_row_counts[index]) == \
                    self.control.total_row_counts[index]:
                self.db_op.delete_rows_except_nos_async(
                    index=index,
                    except_nos=self.control.unselected_row[index].copy(),
                    callback=lambda success, error: self.on_delete_complete(index, success, error)
                )
            else:
                self.db_op.delete_rows_by_nos_async(
                    index=index,
                    nos_set=self.control.selected_row[index].copy(),
                    callback=lambda success, error: self.on_delete_complete(index, success, error)
                )

    def on_delete_complete(self, index, success, error):
        if success:
            self.control.selected_row[index].clear()
            self.control.unselected_row[index].clear()
            self.control.selected_row_counts[index] = 0
            self.control.table_checkboxes[index].value = False

            self.update_table_pages_count()

            current_page = self.control.tables.controls[index].data['page']
            self.db_op.get_table_total_count_async(
                index=index,
                callback=lambda total: self.refresh_after_delete(index, current_page, total)
            )

    def refresh_after_delete(self, index, current_page, total):
        limit = self.control.tables.controls[index].data['limit']
        last_page = (total + limit - 1) // limit if total > 0 else 1

        if current_page > last_page:
            self.control.tables.controls[index].data['page'] = last_page

        self.display_table_data(index)
        self.control.total_row_counts[index] = total

    def deletion_dialog(self):
        dialog = ft.AlertDialog(
            modal=True,
            content=ft.Text(
                value=self.config.RESC['text']['delete']['log'],
            ),
            actions=[
                ft.TextButton(
                    text=f"{self.config.RESC['text']['cancel']}",
                    on_click=lambda e: self.page.close(dialog)),
                ft.TextButton(
                    text=f"{self.config.RESC['text']['confirm']}",
                    on_click=lambda e: self.delete_selected_rows(dialog)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        )
        self.page.open(dialog)

    def export_selected_rows(self):
        index = self.control.table_tab_bar.selected_index

        if self.control.table_checkboxes[index].value:
            self.file_op.export_all_log_data(index)
        elif self.control.selected_row_counts[index] != 0:
            if (len(self.control.unselected_row[index]) + self.control.selected_row_counts[index]) == \
                    self.control.total_row_counts[index]:
                self.file_op.export_log_data_exclude_nos(index, self.control.unselected_row[index])
            else:
                self.file_op.export_log_data_include_nos(index, self.control.selected_row[index])


class Control(AbstractUI):
    def __init__(self, panel: Panel):
        super().__init__()
        self.panel = panel
        self.selected_row = [set(), set(), set()]
        self.unselected_row = [set(), set(), set()]
        self.current_row_checkboxes = []
        self.table_checkboxes = []
        self.total_row_counts = [0, 0, 0]
        self.selected_row_counts = [0, 0, 0]
        self.table_tab_bar = self.init_table_tab_bar()
        self.recv_data_table = self.init_recv_data_table()
        self.user_actions_table = self.init_user_actions_table()
        self.system_events_table = self.init_system_events_table()
        self.current_page_text = self.init_current_page_text()
        self.table_page_controller = self.init_table_page_controller()
        self.log_operation_btn = self.init_log_operation_btn()
        self.tables = self.init_tables()
        self.table_window = self.init_table_window()
        self.log_panel = self.init_log_panel()

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

    def init_recv_data_table(self):
        checkbox = ft.Checkbox(
            value=False,
            width=5
        )
        checkbox.on_change = lambda e: self.panel.update_table_selection(0, checkbox)
        self.table_checkboxes.append(checkbox)

        selector = [ft.DataColumn(label=checkbox)]
        columns = [
            ft.DataColumn(label=ft.Text(name, theme_style=ft.TextThemeStyle.LABEL_SMALL))
            for name in ['No.', 'Timestamp', 'Address', 'Channels', 'HID', 'Detector', 'Data', 'Row Data']
        ]
        return ft.DataTable(
            columns=selector + columns,
            rows=[],
            expand=True
        )

    def init_user_actions_table(self):
        checkbox = ft.Checkbox(
            value=False,
            width=5
        )
        checkbox.on_change = lambda e: self.panel.update_table_selection(1, checkbox)
        self.table_checkboxes.append(checkbox)

        selector = [ft.DataColumn(label=checkbox)]
        columns = [
            ft.DataColumn(label=ft.Text(name, theme_style=ft.TextThemeStyle.LABEL_SMALL))
            for name in ['No.', 'Timestamp', 'Action', 'Payload', 'Target Address', 'Target Channels', 'Target HID']
        ]
        return ft.DataTable(
            columns=selector + columns,
            rows=[],
            expand=True
        )

    def init_system_events_table(self):
        checkbox = ft.Checkbox(
            value=False,
            width=5
        )
        checkbox.on_change = lambda e: self.panel.update_table_selection(2, checkbox)
        self.table_checkboxes.append(checkbox)

        selector = [ft.DataColumn(label=checkbox)]
        columns = [
            ft.DataColumn(label=ft.Text(name, theme_style=ft.TextThemeStyle.LABEL_SMALL))
            for name in ['No.', 'Timestamp', 'Event', 'Detail']
        ]
        return ft.DataTable(
            columns=selector + columns,
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
            on_click=lambda e: self.panel.display_first_page()
        )
        prev_btn = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            on_click=lambda e: self.panel.display_previous_page()
        )
        next_btn = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            on_click=lambda e: self.panel.display_next_page()
        )
        last_page_btn = ft.IconButton(
            icon=ft.Icons.LAST_PAGE,
            on_click=lambda e: self.panel.display_last_page()
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

    def init_log_operation_btn(self):
        def sub_btn(icon, text, handler):
            return ft.MenuItemButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=icon,
                            scale=0.5,
                            color=ft.Colors.PRIMARY
                        ),
                        ft.Text(
                            value=text,
                            theme_style=ft.TextThemeStyle.LABEL_SMALL,
                        ),
                    ],
                    width=100,
                ),
                on_click=handler
            )

        text = self.config.RESC['op']['log']
        return ft.SubmenuButton(
            content=ft.Text(
                value=text['name'],
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                text_align=ft.TextAlign.CENTER,
            ),
            controls=[
                sub_btn(ft.Icons.DELETE,
                        text['del'],
                        lambda e: self.panel.deletion_dialog()),
                sub_btn(ft.Icons.UPLOAD,
                        text['exp'],
                        lambda e: self.panel.export_selected_rows())
            ],
            width=100
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
        bottom_bar = ft.Row(
            controls=[
                ft.Container(expand=1),
                self.table_page_controller,
                ft.Container(
                    content=self.log_operation_btn,
                    alignment=ft.alignment.center_right,
                    expand=1
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Column(
            controls=[
                self.table_tab_bar,
                self.table_window,
                bottom_bar
            ],
            expand=True
        )

    def recording_checkbox(self, data, index):
        checkbox = ft.Checkbox(width=5)
        if self.table_checkboxes[index].value:
            checkbox.value = True
        elif self.selected_row_counts[index] != 0:
            if (len(self.unselected_row[index]) + self.selected_row_counts[index]) == self.total_row_counts[index]:
                checkbox.value = data['no'] not in self.unselected_row[index]
            else:
                checkbox.value = data['no'] in self.selected_row[index]
        else:
            checkbox.value = False
        checkbox.on_change = lambda e: self.panel.update_selected_row(data['no'], index, checkbox)
        return checkbox

    def recv_data_row(self, data, index):
        checkbox = self.recording_checkbox(data, index)
        self.current_row_checkboxes.append(checkbox)
        return ft.DataRow(
            cells=[
                ft.DataCell(checkbox),
                ft.DataCell(ft.Text(data['no'], width=80)),
                ft.DataCell(ft.Text(data['timestamp'], width=100)),
                ft.DataCell(ft.Text(data['address'], width=120)),
                ft.DataCell(ft.Text(data['channels'], width=100)),
                ft.DataCell(ft.Text(data['hid'], width=100)),
                ft.DataCell(ft.Text(data['detector'], width=100)),
                ft.DataCell(ft.Text(data['data'], width=200)),
                ft.DataCell(ft.Text(data['raw_data'], width=200),
                            on_tap=lambda e: self.panel.copy_raw_data_to_clipboard(data['raw_data'])),
            ]
        )

    def user_actions_row(self, data, index):
        checkbox = self.recording_checkbox(data, index)
        self.current_row_checkboxes.append(checkbox)
        return ft.DataRow(
            cells=[
                ft.DataCell(checkbox),
                ft.DataCell(ft.Text(data['no'], width=80)),
                ft.DataCell(ft.Text(data['timestamp'], width=180)),
                ft.DataCell(ft.Text(data['action'], width=120)),
                ft.DataCell(ft.Text(data['payload'], width=400),
                            on_tap=lambda e: self.panel.copy_data_cell_to_clipboard(data['payload'])),
                ft.DataCell(ft.Text(data['target_address'], width=120)),
                ft.DataCell(ft.Text(data['target_channels'], width=100)),
                ft.DataCell(ft.Text(data['target_hid'], width=100))
            ]
        )

    def system_events_row(self, data, index):
        checkbox = self.recording_checkbox(data, index)
        self.current_row_checkboxes.append(checkbox)
        return ft.DataRow(
            cells=[
                ft.DataCell(checkbox),
                ft.DataCell(ft.Text(data['no'], width=80)),
                ft.DataCell(ft.Text(data['timestamp'], width=180)),
                ft.DataCell(ft.Text(data['event'], width=100)),
                ft.DataCell(ft.Text(data['detail'], width=1000),
                            on_tap=lambda e: self.panel.copy_data_cell_to_clipboard(data['detail'])),
            ]
        )
