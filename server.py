import socket
import sqlite3
import json

class DB:
    def __init__(self):
        conn = sqlite3.connect('resources.db')
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS client_resources(
                    id INTEGER PRIMARY KEY,
                    client_ip TEXT,
                    client_hostname TEXT,
                    ip_type TEXT,
                    cpu_usage float,
                    memory_usage float,
                    bytes_sent INT,
                    bytes_recv INT,
                    disk_usage float
                    )''')
    def save_client_data(self, data: dict):
        data = json.loads(data)
        columns = ', '.join(list(data.keys()))
        placeholders = ', '.join(['?' for _ in data.values()])
        values = tuple(data.values())
        query = f'INSERT into client_resources({columns}) VALUES ({placeholders})'
        self.cur.execute(query, values)
        self.conn.commit()


def main():
    db = DB()
    host = ''
    port = 4000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)

    while True:
        conn, address = server.accept()
        print(f"Connection from: {address}")
        while conn:
            try:
                client_message = conn.recv(1024).decode()
                print(f"From client: {client_message}")
                message = f"Json from client: {client_message}"
                conn.send(message.encode())
            except (BrokenPipeError, ConnectionResetError):
                print("-- Client disconnected --")
                break
    server.close()
    db.conn.close()

if __name__ == '__main__':
    main()
