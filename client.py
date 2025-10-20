import socket
import time
from monitor import get_system_resource_usage

host = "10.0.0.123"  # Pi’s static IP
port = 4000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
print("Connected to server")

try:
    while True:
        info = get_system_resource_usage()
        message = "Test message"
        client.send(info.encode())
        server_response = client.recv(1024).decode()
        print(f"From server: {server_response}")
        time.sleep(1)  # send once per second (avoid spamming)
except KeyboardInterrupt:
    print("Client closing connection")
finally:
    client.close()

