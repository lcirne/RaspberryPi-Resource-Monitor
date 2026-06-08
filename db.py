import sqlite3
import time
from pathlib import Path
from threading import Lock
from typing import Optional, Union


MetricValue = Union[str, int, float]


class DB:
    TABLE_COLS = [
        "id",
        "observed_at",
        "client_ip",
        "client_hostname",
        "ip_type",
        "cpu_usage",
        "memory_usage",
        "total_memory",
        "disk_usage",
        "total_disk",
        "bytes_sent",
        "bytes_recv",
        "net_sent_rate",
        "net_recv_rate",
    ]

    WRITABLE_COLS = set(TABLE_COLS) - {"id"}

    def __init__(self, db_path: str = "resources.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.lock = Lock()
        self._init_schema()

    def _init_schema(self) -> None:
        with self.lock:
            self.cur.execute(
                """
                CREATE TABLE IF NOT EXISTS client_resources(
                    id INTEGER PRIMARY KEY,
                    observed_at REAL,
                    client_ip TEXT,
                    client_hostname TEXT,
                    ip_type TEXT,
                    cpu_usage REAL,
                    memory_usage REAL,
                    total_memory REAL,
                    disk_usage REAL,
                    total_disk REAL,
                    bytes_sent INTEGER,
                    bytes_recv INTEGER,
                    net_sent_rate REAL,
                    net_recv_rate REAL
                )
                """
            )
            existing = {
                row["name"]
                for row in self.cur.execute("PRAGMA table_info(client_resources)")
            }
            migrations = {
                "observed_at": "ALTER TABLE client_resources ADD COLUMN observed_at REAL",
                "total_disk": "ALTER TABLE client_resources ADD COLUMN total_disk REAL",
                "net_sent_rate": "ALTER TABLE client_resources ADD COLUMN net_sent_rate REAL",
                "net_recv_rate": "ALTER TABLE client_resources ADD COLUMN net_recv_rate REAL",
            }
            for column, statement in migrations.items():
                if column not in existing:
                    self.cur.execute(statement)
            self.conn.commit()

    def save_client_data(self, data: dict[str, MetricValue]) -> bool:
        if not isinstance(data, dict):
            return False

        payload = {
            key: value
            for key, value in data.items()
            if key in self.WRITABLE_COLS and value is not None
        }
        payload.setdefault("observed_at", time.time())

        try:
            columns = ", ".join(payload.keys())
            placeholders = ", ".join(["?"] * len(payload))
            values = tuple(payload.values())
            query = f"INSERT INTO client_resources({columns}) VALUES ({placeholders})"
            with self.lock:
                self.cur.execute(query, values)
                self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"--- A critical error occurred while saving client data: {e}")
            return False

    def list_clients(self) -> list[dict]:
        query = """
            SELECT cr.*
            FROM client_resources cr
            INNER JOIN (
                SELECT client_ip, MAX(id) AS max_id
                FROM client_resources
                WHERE client_ip IS NOT NULL
                GROUP BY client_ip
            ) latest ON cr.client_ip = latest.client_ip AND cr.id = latest.max_id
            ORDER BY cr.client_hostname COLLATE NOCASE, cr.client_ip
        """
        try:
            with self.lock:
                rows = self.cur.execute(query).fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"--- A critical error occurred while listing clients: {e}")
            return []

    def get_latest_client_data(self, client_ip: Optional[str] = None) -> Optional[dict]:
        if client_ip:
            query = """
                SELECT * FROM client_resources
                WHERE client_ip = ?
                ORDER BY id DESC
                LIMIT 1
            """
            params = (client_ip,)
        else:
            query = "SELECT * FROM client_resources ORDER BY id DESC LIMIT 1"
            params = ()

        try:
            with self.lock:
                row = self.cur.execute(query, params).fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"--- A critical error occurred while fetching latest client data: {e}")
            return None

    def get_client_data(self, ip: str, num_records: int = 60) -> list[dict]:
        query = """
            SELECT * FROM client_resources
            WHERE client_ip = ?
            ORDER BY id DESC
            LIMIT ?
        """
        try:
            with self.lock:
                records = self.cur.execute(query, (ip, num_records)).fetchall()
            return [dict(row) for row in reversed(records)]
        except sqlite3.Error as e:
            print(f"--- A critical error occurred while fetching client data: {e}")
            return []

    def extract_field_from_data(
        self,
        field: str,
        records: list[dict],
        num_records: int = 60,
    ) -> list[float]:
        record_values = [float(record.get(field) or 0) for record in records]
        while len(record_values) < num_records:
            record_values.insert(0, 0)
        return record_values

    def close(self) -> None:
        self.conn.close()


if __name__ == "__main__":
    db = DB()
    print(db.list_clients())
