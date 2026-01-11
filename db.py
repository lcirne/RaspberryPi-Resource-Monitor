import sqlite3
import json
from typing import Optional, Union

class DB:
    def __init__(self):
        self.conn = sqlite3.connect('resources.db')
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS client_resources(
                    id INTEGER PRIMARY KEY,
                    client_ip TEXT,
                    client_hostname TEXT,
                    ip_type TEXT,
                    cpu_usage float,
                    memory_usage float,
                    total_memory float,
                    bytes_sent INT,
                    bytes_recv INT,
                    disk_usage float
                    )''')

    def save_client_data(self, data: dict[str, Union[str, int, float]]) -> bool:
        try:
            columns = ', '.join(list(data.keys()))
            placeholders = ', '.join(['?' for _ in data.values()])
            values = tuple(data.values())
            query = f'INSERT into client_resources({columns}) VALUES ({placeholders})'
            self.cur.execute(query, values)
            self.conn.commit()
            return True
        except (AttributeError, sqlite3.Error) as e:
            print(f'--- A critical error occurred while saving client data: {e}')
            return False


    def get_client_data(self, ip: str, num_records=15) -> Optional[list[dict]]:
        '''Fetch a certain number of database records for a given ip'''
        TABLE_COLS = ['id', 'client_ip', 'client_hostname', 'ip_type', 'cpu_usage',
                        'memory_usage', 'total_memory', 'bytes_sent', 'bytes_recv', 'disk_usage']
        try:
            query = f'''SELECT * FROM client_resources 
            WHERE client_ip == ? 
            ORDER BY id DESC
            LIMIT {num_records};'''
            self.cur.execute(query, (ip,))
            records = self.cur.fetchall()

            client_data = []
            if records:
                for record in records:
                    # Appends records newest to olders
                    data = dict(zip(TABLE_COLS, record))
                    client_data.append(data)

            # Return records oldest to newest for easier interactive graphing later
            return list(reversed(client_data))
        except sqlite3.Error as e:
            print(f'--- A critical error occurred while fetching client data: {e}')
            return None


    def extract_field_from_data(self,
                                field: str,
                                records: list[dict],
                                num_records=15) -> list[float]:
        '''Return 15 values for a certain field in the database for graphing'''
        record_values = []
        for record in records:
            record_values.append(record.get(field))
        while len(record_values) < num_records:
            record_values.insert(0, 0)
        return record_values


if __name__=='__main__':
    db = DB()
    client_data = db.get_client_data("192.168.68.51")
    client_ram_usage = db.extract_field_from_data('memory_usage', client_data)
    print(client_ram_usage)
