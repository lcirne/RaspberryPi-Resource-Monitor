import socket

host = "10.245.3.174"
port = 4000

server = socket.socket()
server.bind((host, port))
server.listen(1)
conn, address = server.accept()
print(f"Connection from: {address}")

while True:
    client_message = conn.recv(1024).decode()
    print(f"From client: {client_message}")
    message = f"Json from client: {client_message}"
    conn.send(message.encode())
server.close()
