import socket
import sqlite3
import json
from db import DB

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
                print("Saving client data...")
                db.save_client_data(json.loads(client_message))
                print("Saved!")
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
