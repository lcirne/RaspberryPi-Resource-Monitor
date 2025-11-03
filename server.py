import socket
import sqlite3

def save_usage_data(data_json):



def main():
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

if __name__ == '__main__':
    main()
