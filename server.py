import socket
import sqlite3
import json
import numpy as np
from db import DB
from grapher import Grapher

def main():
    db = DB()
    grapher = Grapher()
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
                client_message = json.loads(client_message)
                db.save_client_data(client_message)
                print("Saved!")
                print(f"From client: {json.dumps(client_message, indent=4)}")
                message = f"Json from client: {client_message}"
                conn.send(message.encode())

                # Pull client data from db
                client_ip = client_message.get("client_ip")
                client_data = db.get_client_data(client_ip)
                cpu_usage = db.extract_field_from_data('cpu_usage', client_data)
                ram_usage = db.extract_field_from_data('memory_usage', client_data)
                total_ram = db.extract_field_from_data('total_memory', client_data)
                bytes_sent = db.extract_field_from_data('bytes_sent', client_data)

                # Graph client data
                grapher.graph_cpu_usage(cpu_usage)
                grapher.graph_ram_usage(ram_usage, total_ram)
                grapher.graph_network_usage(bytes_sent)

            except (BrokenPipeError, ConnectionResetError):
                print("-- Client disconnected --")
                break
    server.close()
    db.conn.close()

if __name__ == '__main__':
    main()
