import sqlite3 as sql
import threading
from concurrent.futures import ThreadPoolExecutor
from Script.Data import USBEvent, Formatter


class Operator:
    data_ft = Formatter()

    def __init__(self, evt_bcst, config):
        self.bcst = evt_bcst
        self.config = config
        self.database_path = self.config.DATABASE
        self.local = threading.local()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.init_log_db()
        self.subscribe_event()

    def __del__(self):
        if hasattr(self.local, 'log_db'):
            self.local.log_db.close()
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

    def get_db_connection(self):
        if not hasattr(self.local, 'log_db'):
            self.local.log_db = sql.connect(self.database_path['log'], timeout=10)
        return self.local.log_db

    def init_log_db(self):
        conn = sql.connect(self.database_path['log'])
        self.init_recv_data_table(conn)
        self.init_user_action_table(conn)
        self.init_system_events_table(conn)
        conn.close()

    def subscribe_event(self):
        self.bcst.subscribe(self.on_recv_data, 'recv')
        self.bcst.subscribe(self.on_scan_finish, 'scan_fin')
        self.bcst.subscribe(self.on_attack_finish, 'atk_fin')
        self.bcst.subscribe(self.on_error, 'error')

    def on_recv_data(self, event):
        try:
            if isinstance(event, USBEvent):
                report = event.device['report']
                timestamp = report['timestamp']
                channels = self.data_ft.form_list(report['channels'], ',')
                address = self.data_ft.form_hex_list(report['address'][::-1], ':')
                hid = report['device'].description() if report['device'] else 'Unknown'
                data = self.data_ft.form_hex_list(report['payload'], ':')
                raw_data = bytes(report['payload'])
                detector = report['detector']
                self.insert_recv_data_async(timestamp, address, channels, hid, data, raw_data, detector)
        except Exception as e:
            self.insert_system_event_async(self.data_ft.form_timestamp_str_in_year(),
                                           'DB Insertion Error on Recv Data', str(e))

    def on_scan_finish(self, event):
        try:
            if isinstance(event, USBEvent):
                report = event.device['report']
                timestamp = str(report['timestamp'])
                action = str(report['action'])
                payload = str(report['payload'])
                target_address = report['target_address']
                target_channels = report['target_channels']
                target_hid = report['target_hid']
                self.insert_user_action_async(timestamp, action, payload, target_address, target_channels, target_hid)
        except Exception as e:
            self.insert_system_event_async(self.data_ft.form_timestamp_str_in_year(),
                                           'DB Insertion Error on Scan Finish', str(e))

    def on_attack_finish(self, event):
        try:
            if isinstance(event, USBEvent):
                report = event.device['report']
                timestamp = str(report['timestamp'])
                action = str(report['action'])
                payload = str(report['payload'])
                target_address = self.data_ft.form_address_list(report['target_address'])
                target_channels = self.data_ft.form_channels_list(report['target_channels'])
                target_hid = self.data_ft.form_hid_list(report['target_hid'])
                self.insert_user_action_async(timestamp, action, payload, target_address, target_channels, target_hid)
        except Exception as e:
            self.insert_system_event_async(self.data_ft.form_timestamp_str_in_year(),
                                           'DB Insertion Error on Attack Finish', str(e))

    def on_error(self, event):
        try:
            if isinstance(event, USBEvent):
                report = event.device['report']
                timestamp = str(report['timestamp'])
                event = str(report['event'])
                detail = str(report['detail'])
                self.insert_system_event_async(timestamp, event, detail)
        except Exception as e:
            self.insert_system_event_async(self.data_ft.form_timestamp_str_in_year(),
                                           'DB Insertion Error on Error Report', str(e))

    def insert_recv_data_async(self, timestamp, address, channels, hid, data, raw_data, detector):

        def insert():
            try:
                self.insert_recv_data(timestamp, address, channels, hid, data, raw_data, detector)
            except Exception as e:
                self.insert_system_event_async(self.data_ft.form_timestamp_str_in_year(),
                                               'DB Async Insertion Error on Recv Data', str(e))

        thread = threading.Thread(target=insert, daemon=True)
        thread.start()

    def insert_user_action_async(self, timestamp, action, payload, target_address, target_channels, target_hid):

        def insert():
            try:
                self.insert_user_action(timestamp, action, payload, target_address, target_channels, target_hid)
            except Exception as e:
                self.insert_system_event_async(self.data_ft.form_timestamp_str_in_year(),
                                               'DB Async Insertion Error on User Action', str(e))

        thread = threading.Thread(target=insert, daemon=True)
        thread.start()

    def insert_system_event_async(self, timestamp, event, detail):

        def insert():
            try:
                self.insert_system_event(timestamp, event, detail)
            except Exception as e:
                print(f'DB Async Insertion Error on System Event: {str(e)}')

        thread = threading.Thread(target=insert, daemon=True)
        thread.start()

    @staticmethod
    def init_recv_data_table(conn):
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS received_data (
                            id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,    
                            no INTEGER NOT NULL,                
                            timestamp TEXT NOT NULL,
                            address TEXT NOT NULL,               
                            channels TEXT,                         
                            hid TEXT,                             
                            data TEXT,                            
                            raw_data BLOB,                    
                            detector TEXT NOT NULL)''')
        conn.commit()
        cursor.close()

    @staticmethod
    def init_user_action_table(conn):
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_actions (
                            id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,    
                            no INTEGER NOT NULL,         
                            timestamp TEXT NOT NULL,
                            action TEXT,
                            payload TEXT,
                            target_address TEXT NOT NULL,               
                            target_channels TEXT,                         
                            target_hid TEXT)''')
        conn.commit()
        cursor.close()

    @staticmethod
    def init_system_events_table(conn):
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS system_events (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,  
                            no INTEGER NOT NULL,           
                            timestamp TEXT NOT NULL,
                            event TEXT NOT NULL,
                            detail TEXT)''')
        conn.commit()
        cursor.close()

    def init_log_db_for_recv(self):
        conn = self.get_db_connection()
        self.init_recv_data_table(conn)

    def init_log_db_for_action(self):
        conn = self.get_db_connection()
        self.init_user_action_table(conn)

    def init_log_db_for_system(self):
        conn = self.get_db_connection()
        self.init_system_events_table(conn)

    def insert_recv_data(self, timestamp, address, channels, hid, data, raw_data, detector):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            no = self.get_table_count(cursor, 'received_data') + 1
            cursor.execute(
                '''
                INSERT INTO received_data (no, timestamp, address, channels, hid, data, raw_data, detector)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (no, timestamp, address, channels, hid, data, raw_data, detector)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.insert_system_event_async(self.data_ft.form_timestamp_str_in_year(),
                                           'DB Error on Recv Data Insertion', str(e))
        finally:
            cursor.close()

    def insert_user_action(self, timestamp, action, payload, target_address, target_channels, target_hid):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            no = self.get_table_count(cursor, 'user_actions') + 1
            cursor.execute(
                '''
                INSERT INTO user_actions (no, timestamp, action, payload, target_address, target_channels, target_hid)
                VALUES  (?, ?, ?, ?, ?, ?, ?)
                ''', (no, timestamp, action, payload, target_address, target_channels, target_hid)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.insert_system_event_async(self.data_ft.form_timestamp_str_in_year(),
                                           'DB Error on User Action Insertion', str(e))
        finally:
            cursor.close()

    def insert_system_event(self, timestamp, event, detail):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            no = self.get_table_count(cursor, 'system_events') + 1
            cursor.execute('''
                           INSERT INTO system_events (no, timestamp, event, detail)
                           VALUES (?, ?, ?, ?)
                       ''', (no, timestamp, event, detail))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def get_table_count(cursor, table_name):
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_table_total_count_async(self, index, callback):
        table_names = ['received_data', 'user_actions', 'system_events']
        table_name = table_names[index]

        def count_task():
            conn = self.get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                result = cursor.fetchone()
                total = result[0] if result else 0
                callback(total)
            except Exception as e:
                self.insert_system_event_async(
                    self.data_ft.form_timestamp_str_in_year(),
                    'DB Count Error', str(e)
                )
                callback(0)
            finally:
                cursor.close()

        self.executor.submit(count_task)

    def select_data_by_table_index(self, index, callback=None, start_no=None, end_no=None, limit=None, offset=0,
                                   order_by='no', order_dir='ASC'):
        if index == 0:
            self.select_recv_data(callback, start_no, end_no, limit, offset, order_by, order_dir)
        elif index == 1:
            self.select_user_actions(callback, start_no, end_no, limit, offset, order_by, order_dir)
        elif index == 2:
            self.select_system_events(callback, start_no, end_no, limit, offset, order_by, order_dir)

    def select_data(self, query, start_no=None, end_no=None, limit=None, offset=0, order_by='no', order_dir='ASC'):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            params = []
            conditions = []
            if start_no is not None:
                conditions.append('no >= ?')
                params.append(start_no)
            if end_no is not None:
                conditions.append('no <= ?')
                params.append(end_no)
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            query += f' ORDER BY {order_by} {order_dir}'
            if limit is not None:
                query += ' LIMIT ? OFFSET ?'
                params.append(limit)
                params.append(offset)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            conn.rollback()
            self.insert_system_event_async(self.data_ft.form_timestamp_str_in_year(),
                                           'DB Selection Error', str(e))
            return []
        finally:
            cursor.close()

    def select_recv_data(self, callback=None, start_no=None, end_no=None, limit=None, offset=0, order_by='no',
                         order_dir='ASC'):
        if callback is None:
            return self.select_recv_data_sync(start_no, end_no, limit, offset, order_by, order_dir)
        else:
            self.executor.submit(
                self.select_recv_data_async,
                callback, start_no, end_no, limit, offset, order_by, order_dir
            )

    def select_user_actions(self, callback=None, start_no=None, end_no=None, limit=None, offset=0, order_by='no',
                            order_dir='ASC'):
        if callback is None:
            return self.select_user_actions_sync(start_no, end_no, limit, offset, order_by, order_dir)
        else:
            self.executor.submit(
                self.select_user_actions_async,
                callback, start_no, end_no, limit, offset, order_by, order_dir
            )

    def select_system_events(self, callback=None, start_no=None, end_no=None, limit=None, offset=0, order_by='no',
                             order_dir='ASC'):
        if callback is None:
            return self.select_system_events_sync(start_no, end_no, limit, offset, order_by, order_dir)
        else:
            self.executor.submit(
                self.select_system_events_async,
                callback, start_no, end_no, limit, offset, order_by, order_dir
            )

    def select_recv_data_sync(self, start_no=None, end_no=None, limit=None, offset=0, order_by='no', order_dir='ASC'):
        try:
            rows = self.select_data(
                'SELECT no, timestamp, address, channels, hid, data, raw_data, detector FROM received_data',
                start_no, end_no, limit, offset, order_by, order_dir)
            result = []
            for row in rows:
                result.append({
                    'no': row[0],
                    'timestamp': row[1],
                    'address': row[2],
                    'channels': row[3],
                    'hid': row[4],
                    'data': row[5],
                    'raw_data': list(row[6]) if row[6] else [],
                    'detector': row[7]
                })
            return result
        except Exception as e:
            self.insert_system_event_async(self.data_ft.form_timestamp_str_in_year(),
                                           'DB Error on Recv Data Selection', str(e))
            return []

    def select_user_actions_sync(self, start_no=None, end_no=None, limit=None, offset=0, order_by='no',
                                 order_dir='ASC'):
        try:
            rows = self.select_data(
                'SELECT no, timestamp, action, payload, target_address, target_channels, target_hid FROM user_actions',
                start_no, end_no, limit, offset, order_by, order_dir)
            result = []
            for row in rows:
                result.append({
                    'no': row[0],
                    'timestamp': row[1],
                    'action': row[2],
                    'payload': row[3],
                    'target_address': row[4],
                    'target_channels': row[5],
                    'target_hid': row[6]
                })
            return result
        except Exception as e:
            self.insert_system_event_async(self.data_ft.form_timestamp_str_in_year(),
                                           'DB Error on User Actions Selection', str(e))
            return []

    def select_system_events_sync(self, start_no=None, end_no=None, limit=None, offset=0, order_by='no',
                                  order_dir='ASC'):
        try:
            rows = self.select_data(
                'SELECT no, timestamp, event, detail FROM system_events',
                start_no, end_no, limit, offset, order_by, order_dir)
            result = []
            for row in rows:
                result.append({
                    'no': row[0],
                    'timestamp': row[1],
                    'event': row[2],
                    'detail': row[3]
                })
            return result
        except Exception as e:
            self.insert_system_event_async(self.data_ft.form_timestamp_str_in_year(),
                                           'DB Error on System Events Selection', str(e))
            return []

    def select_recv_data_async(self, callback, start_no=None, end_no=None, limit=None, offset=0, order_by='no',
                               order_dir='ASC'):
        try:
            result = self.select_recv_data_sync(start_no, end_no, limit, offset, order_by, order_dir)
            callback(result)
        except Exception as e:
            callback({'error': str(e)})

    def select_user_actions_async(self, callback, start_no=None, end_no=None, limit=None, offset=0, order_by='no',
                                  order_dir='ASC'):
        try:
            result = self.select_user_actions_sync(start_no, end_no, limit, offset, order_by, order_dir)
            callback(result)
        except Exception as e:
            callback({'error': str(e)})

    def select_system_events_async(self, callback, start_no=None, end_no=None, limit=None, offset=0, order_by='no',
                                   order_dir='ASC'):
        try:
            result = self.select_system_events_sync(start_no, end_no, limit, offset, order_by, order_dir)
            callback(result)
        except Exception as e:
            callback({'error': str(e)})

    def delete_all_rows_async(self, index, callback):
        def delete_task():
            try:
                self.delete_all_rows(index)
                self.reorder_no_field(index)
                callback(True, None)
            except Exception as e:
                self.insert_system_event_async(
                    self.data_ft.form_timestamp_str_in_year(),
                    'DB Delete All Error',
                    str(e)
                )
                callback(False, str(e))

        self.executor.submit(delete_task)

    def delete_rows_by_nos_async(self, index, nos_set, callback):
        def delete_task():
            try:
                self.delete_rows_by_nos(index, nos_set)
                self.reorder_no_field(index)
                callback(True, None)
            except Exception as e:
                self.insert_system_event_async(
                    self.data_ft.form_timestamp_str_in_year(),
                    'DB Delete By Nos Error',
                    str(e)
                )
                callback(False, str(e))

        self.executor.submit(delete_task)

    def delete_rows_except_nos_async(self, index, except_nos, callback):
        def delete_task():
            try:
                self.delete_rows_except_nos(index, except_nos)
                self.reorder_no_field(index)
                callback(True, None)
            except Exception as e:
                self.insert_system_event_async(
                    self.data_ft.form_timestamp_str_in_year(),
                    'DB Delete Except Nos Error',
                    str(e)
                )
                callback(False, str(e))

        self.executor.submit(delete_task)

    def delete_all_rows(self, index):
        table_name = self.get_table_name_by_index(index)
        conn = self.get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(f'DELETE FROM {table_name}')
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def delete_rows_by_nos(self, index, nos_set):
        if not nos_set:
            return

        table_name = self.get_table_name_by_index(index)
        conn = self.get_db_connection()
        cursor = conn.cursor()

        try:
            placeholders = ','.join(['?' for _ in nos_set])
            query = f'DELETE FROM {table_name} WHERE no IN ({placeholders})'
            cursor.execute(query, list(nos_set))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def delete_rows_except_nos(self, index, except_nos_set):
        if not except_nos_set:
            self.delete_all_rows(index)
            return

        table_name = self.get_table_name_by_index(index)
        conn = self.get_db_connection()
        cursor = conn.cursor()

        try:
            placeholders = ','.join(['?' for _ in except_nos_set])
            query = f'DELETE FROM {table_name} WHERE no NOT IN ({placeholders})'
            cursor.execute(query, list(except_nos_set))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def reorder_no_field(self, index):
        table_name = self.get_table_name_by_index(index)
        conn = self.get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]

            if count == 0:
                return

            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            version_tuple = tuple(map(int, version.split('.')))

            if version_tuple >= (3, 25, 0):
                self.reorder_with_window_function(index, table_name, cursor)
            else:
                self.reorder_without_window_function(index, table_name, cursor)

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def reorder_with_window_function(index, table_name, cursor):
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        select_parts = ['id', 'ROW_NUMBER() OVER (ORDER BY id) as new_no']
        for col in column_names:
            if col not in ['id', 'no']:
                select_parts.append(col)

        temp_table = f'temp_{table_name}'
        select_sql = f'SELECT {", ".join(select_parts)} FROM {table_name}'
        cursor.execute(f'CREATE TEMPORARY TABLE {temp_table} AS {select_sql}')

        cursor.execute(f'DELETE FROM {table_name}')

        insert_columns = ['id', 'no'] + [col for col in column_names if col not in ['id', 'no']]
        insert_sql = f'''
                INSERT INTO {table_name} ({", ".join(insert_columns)})
                SELECT {", ".join(select_parts)} FROM {temp_table}
                ORDER BY new_no
            '''
        cursor.execute(insert_sql)
        cursor.execute(f'DROP TABLE {temp_table}')

    @staticmethod
    def reorder_without_window_function(index, table_name, cursor):
        cursor.execute(f'SELECT id FROM {table_name} ORDER BY id')
        ids = cursor.fetchall()

        for new_no, (row_id,) in enumerate(ids, 1):
            cursor.execute(f'UPDATE {table_name} SET no = ? WHERE id = ?', (new_no, row_id))

    @staticmethod
    def get_table_name_by_index(index):
        table_names = ['received_data', 'user_actions', 'system_events']
        return table_names[index]

    def get_last_no(self, index):
        table_name = self.get_table_name_by_index(index)
        conn = self.get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(f'SELECT MAX(no) FROM {table_name}')
            result = cursor.fetchone()
            return result[0] if result and result[0] else 0
        except Exception as e:
            return 0
        finally:
            cursor.close()

    def get_all_data_sync(self, index):
        if index == 0:
            return self.select_recv_data_sync()
        elif index == 1:
            return self.select_user_actions_sync()
        elif index == 2:
            return self.select_system_events_sync()
        return []

    def get_data_by_nos_sync(self, index, nos_set):
        if not nos_set:
            return []

        placeholders = ','.join(['?' for _ in nos_set])

        if index == 0:
            query = f'''
                SELECT no, timestamp, address, channels, hid, data, raw_data, detector
                FROM received_data 
                WHERE no IN ({placeholders})
                ORDER BY no
            '''
            rows = self.execute_query_sync(query, list(nos_set))
            return [{
                'no': row[0],
                'timestamp': row[1],
                'address': row[2],
                'channels': row[3],
                'hid': row[4],
                'data': row[5],
                'raw_data': list(row[6]) if row[6] else [],
                'detector': row[7]
            } for row in rows]

        elif index == 1:
            query = f'''
                SELECT no, timestamp, action, payload, target_address, target_channels, target_hid
                FROM user_actions 
                WHERE no IN ({placeholders})
                ORDER BY no
            '''
            rows = self.execute_query_sync(query, list(nos_set))
            return [{
                'no': row[0],
                'timestamp': row[1],
                'action': row[2],
                'payload': row[3],
                'target_address': row[4],
                'target_channels': row[5],
                'target_hid': row[6]
            } for row in rows]

        elif index == 2:
            query = f'''
                SELECT no, timestamp, event, detail
                FROM system_events 
                WHERE no IN ({placeholders})
                ORDER BY no
            '''
            rows = self.execute_query_sync(query, list(nos_set))
            return [{
                'no': row[0],
                'timestamp': row[1],
                'event': row[2],
                'detail': row[3]
            } for row in rows]

        return []

    def get_data_except_nos_sync(self, index, except_nos_set):
        if except_nos_set is None:
            except_nos_set = set()

        if not except_nos_set:
            return self.get_all_data_sync(index)

        except_list = list(except_nos_set)
        placeholders = ','.join(['?' for _ in except_list])

        if index == 0:
            query = f'''
                SELECT no, timestamp, address, channels, hid, data, raw_data, detector
                FROM received_data 
                WHERE no NOT IN ({placeholders})
                ORDER BY no
            '''
            rows = self.execute_query_sync(query, except_list)
            return [{
                'no': row[0],
                'timestamp': row[1],
                'address': row[2],
                'channels': row[3],
                'hid': row[4],
                'data': row[5],
                'raw_data': list(row[6]) if row[6] else [],
                'detector': row[7]
            } for row in rows]

        elif index == 1:
            query = f'''
                SELECT no, timestamp, action, payload, target_address, target_channels, target_hid
                FROM user_actions 
                WHERE no NOT IN ({placeholders})
                ORDER BY no
            '''
            rows = self.execute_query_sync(query, except_list)
            return [{
                'no': row[0],
                'timestamp': row[1],
                'action': row[2],
                'payload': row[3],
                'target_address': row[4],
                'target_channels': row[5],
                'target_hid': row[6]
            } for row in rows]

        elif index == 2:
            query = f'''
                SELECT no, timestamp, event, detail
                FROM system_events 
                WHERE no NOT IN ({placeholders})
                ORDER BY no
            '''
            rows = self.execute_query_sync(query, except_list)
            return [{
                'no': row[0],
                'timestamp': row[1],
                'event': row[2],
                'detail': row[3]
            } for row in rows]

        return []

    def execute_query_sync(self, query, params=None):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            self.insert_system_event_async(
                self.data_ft.form_timestamp_str_in_year(),
                'DB Query Error',
                str(e)
            )
            return []
        finally:
            cursor.close()
