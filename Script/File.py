import threading
import flet as ft
from pathlib import Path
from Script.Data import Formatter
from Script.Database.SQLite import Operator
from openpyxl.styles import Font, Alignment


class File:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, page: ft.Page, config, data_ft: Formatter, db_op: Operator):
        self.page = page
        self.config = config
        self.data_ft = data_ft
        self.db_op = db_op
        self.file_save_picker = ft.FilePicker()
        self.file_open_picker = ft.FilePicker()
        self.init()

    def init(self):
        self.page.overlay.extend([self.file_save_picker, self.file_open_picker])

    def open_file(self, e, extensions: list, content_widget):
        self.file_open_picker.on_result = lambda event: self.read_file(event, content_widget)
        self.file_open_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=extensions
        )

    def save_file(self, e, name: str, extensions: list, content_widget):
        self.file_save_picker.on_result = lambda event: self.write_file(event, content_widget)
        self.file_save_picker.save_file(
            file_name=name,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=extensions
        )

    def read_file(self, e: ft.FilePickerResultEvent, text: ft.TextField):
        if e.files and len(e.files) > 0:
            file = e.files[0]
            try:
                with open(file.path, 'r', encoding='utf-8') as f:
                    text.value = f.read()
            except Exception as ex:
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text(
                            value=f"Failed to read file: {ex}",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        duration=2000,
                        bgcolor=self.config.FIXED_COLORS['warning'],
                    )
                )
            self.page.update()

    def write_file(self, e: ft.FilePickerResultEvent, content_widget):
        if e.path:
            try:
                content = content_widget.value if isinstance(content_widget, ft.TextField) else str(content_widget)
                with open(e.path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text(value=f"File saved to: {e.path}",
                                        text_align=ft.TextAlign.CENTER),
                        duration=2000,
                    )
                )
            except Exception as ex:
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text(value=f"Failed to save file: {ex}"),
                        duration=2000,
                        bgcolor=self.config.FIXED_COLORS['warning'],
                    )
                )
            self.page.update()

    def import_yaml_file(self, e, callback=None):
        self.file_open_picker.on_result = lambda event: self.handle_theme_import(event, callback)
        self.file_open_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=['yml', 'yaml']
        )

    def handle_theme_import(self, e: ft.FilePickerResultEvent, callback):
        if e.files and len(e.files) > 0:
            file = e.files[0]
            file_name = f'{Path(file.name).stem}.yml'
            try:
                with open(file.path, 'r', encoding='utf-8') as f:
                    theme_file = f.read()
                file_path = self.config.THEME_PATH / file_name
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(theme_file)
                self.config.add_theme_style(file_name)
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text(f"File Importing Succeed: {file_name}.",
                                        text_align=ft.TextAlign.CENTER),
                        duration=2000,
                    )
                )
                if callback:
                    callback()
            except Exception as ex:
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text(f"File Importing Failed: {ex}"),
                        duration=2000,
                        bgcolor=self.config.FIXED_COLORS['warning'],
                    )
                )
            self.page.update()

    def delete_file(self, file_name, file_path, callback=None, reload=None):
        try:
            if not file_path.exists():
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text(f"File not found: {file_name}"),
                        duration=2000,
                        bgcolor=self.config.FIXED_COLORS['warning'],
                    )
                )
                return
            file_path.unlink()
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"File deleted: {file_name}"),
                    duration=2000,
                )
            )
            if callback:
                callback()
            if reload:
                reload()
        except Exception as ex:
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"Failed to delete file: {ex}"),
                    duration=2000,
                    bgcolor=self.config.FIXED_COLORS['warning'],
                )
            )
        self.page.update()

    def delete_theme_file(self, file_name: str):
        file_path = Path(self.config.THEME_PATH / file_name)
        self.delete_file(file_name, file_path)

    def import_plugin_file(self, e, dict_name, callback=None, reload=None):
        self.file_open_picker.on_result = lambda event: self.handle_plugin_import(event, callback, dict_name, reload)
        self.file_open_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=['py'],
        )

    def handle_plugin_import(self, e: ft.FilePickerResultEvent, callback, dict_name: str, reload):
        if e.files and len(e.files) > 0:
            file = e.files[0]
            try:
                with open(file.path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    is_valid, error_msg = self.data_ft.validate_plugin(content, file.name, dict_name)
                    if is_valid:
                        hid_plugin_path = self.config.PLUGIN_PATH / dict_name / file.name
                        if hid_plugin_path.exists():
                            self.page.open(
                                ft.SnackBar(
                                    content=ft.Text(f"Plugin file already exists: {file.name}"),
                                    duration=3000,
                                    bgcolor=self.config.FIXED_COLORS['warning'],
                                )
                            )
                            return
                        with open(hid_plugin_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self.page.open(
                            ft.SnackBar(
                                content=ft.Text(f"Plugin imported successfully: {file.name}"),
                                duration=2000,
                            )
                        )
                        if callback:
                            callback()
                        if reload:
                            reload()
                    else:
                        self.page.open(
                            ft.SnackBar(
                                content=ft.Text(f"Invalid plugin: {error_msg}"),
                                duration=3000,
                                bgcolor=self.config.FIXED_COLORS['warning'],
                            )
                        )
            except Exception as ex:
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text(f"Failed to register plugin: {ex}"),
                        duration=2000,
                        bgcolor=self.config.FIXED_COLORS['warning'],
                    )
                )
            self.page.update()

    def delete_plugin_file(self, dict_name: str, file_name: str, callback=None, reload=None):
        file_path = Path(self.config.PLUGIN_PATH / dict_name / file_name)
        self.delete_file(file_name, file_path, callback, reload)

    def export_all_log_data(self, index):
        self.file_save_picker.on_result = lambda e: self.handle_export(e, index, 'all', None, None)
        self.file_save_picker.save_file(
            file_name=f"{self.config.RESC['op']['log']['file']}",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=['xlsx']
        )

    def export_log_data_exclude_nos(self, index, nos):
        self.file_save_picker.on_result = lambda e: self.handle_export(e, index, 'exclude', nos, None)
        self.file_save_picker.save_file(
            file_name=f"{self.config.RESC['op']['log']['file']}",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=['xlsx']
        )

    def export_log_data_include_nos(self, index, nos):
        self.file_save_picker.on_result = lambda e: self.handle_export(e, index, 'include', None, nos)
        self.file_save_picker.save_file(
            file_name=f"{self.config.RESC['op']['log']['file']}",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=['xlsx']
        )

    def handle_export(self, e: ft.FilePickerResultEvent, index, mode, exclude_nos, include_nos):
        if not e.path:
            return

        threading.Thread(
            target=self.export_data_thread,
            args=(index, mode, exclude_nos, include_nos, e.path),
            daemon=True
        ).start()

    def export_data_thread(self, index, mode, exclude_nos, include_nos, file_path):
        try:
            table_names = ['received_data', 'user_actions', 'system_events']
            table_name = table_names[index]

            if mode == 'all':
                data_list = self.db_op.get_all_data_sync(index)
            elif mode == 'include':
                data_list = self.db_op.get_data_by_nos_sync(index, include_nos)
            elif mode == 'exclude':
                data_list = self.db_op.get_data_except_nos_sync(index, exclude_nos)
            else:
                data_list = []

            if not data_list:
                return

            self.write_to_excel(data_list, file_path, table_name)

        except Exception as ex:
            self.db_op.insert_system_event_async(
                self.data_ft.form_timestamp_str_in_year(),
                'Export Error',
                f"Mode: {mode}, Index: {index}, Error: {str(ex)}"
            )

    @staticmethod
    def write_to_excel(data_list, file_path, sheet_name):
        import pandas as pd
        df = pd.DataFrame(data_list)

        if 'raw_data' in df.columns:
            df['raw_data'] = df['raw_data'].apply(
                lambda x: ' '.join(f'{b:02X}' for b in x) if x else ''
            )

        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]

            for cell in worksheet[1]:
                cell.font = Font(bold=True, color="000000")
                cell.alignment = Alignment(horizontal="center", vertical="center")

            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
