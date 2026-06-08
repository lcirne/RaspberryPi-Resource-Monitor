import argparse
import json
import socket
import threading
from typing import List, Optional, Tuple

from db import DB


class ResourceServer:
    def __init__(self, host: str = "", port: int = 4000, db_path: str = "resources.db"):
        self.host = host
        self.port = port
        self.db_path = db_path
        self._server_socket: Optional[socket.socket] = None
        self._stop_event = threading.Event()
        self._threads: List[threading.Thread] = []

    def serve_forever(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(20)
            server_socket.settimeout(1)
            self._server_socket = server_socket
            print(f"Resource server listening on {self.host or '0.0.0.0'}:{self.port}")

            while not self._stop_event.is_set():
                try:
                    conn, address = server_socket.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break

                thread = threading.Thread(
                    target=self._handle_client,
                    args=(conn, address),
                    daemon=True,
                )
                thread.start()
                self._threads.append(thread)

    def start_in_thread(self) -> threading.Thread:
        thread = threading.Thread(target=self.serve_forever, daemon=True)
        thread.start()
        return thread

    def stop(self) -> None:
        self._stop_event.set()
        if self._server_socket:
            self._server_socket.close()

    def _handle_client(self, conn: socket.socket, address: Tuple[str, int]) -> None:
        db = DB(self.db_path)
        print(f"Connection from {address[0]}:{address[1]}")
        with conn, db.conn:
            buffer = ""
            while not self._stop_event.is_set():
                try:
                    chunk = conn.recv(4096)
                except (ConnectionError, OSError):
                    break

                if not chunk:
                    break

                buffer += chunk.decode("utf-8", errors="replace")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self._save_message(db, line, address[0])

        db.close()
        print(f"Disconnected {address[0]}:{address[1]}")

    def _save_message(self, db: DB, line: str, fallback_ip: str) -> None:
        if not line.strip():
            return

        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"Invalid JSON from client: {exc}")
            return

        if not isinstance(payload, dict):
            return

        payload.setdefault("client_ip", fallback_ip)
        db.save_client_data(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the resource monitor TCP server.")
    parser.add_argument("--host", default="")
    parser.add_argument("--port", type=int, default=4000)
    parser.add_argument("--db", default="resources.db")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ResourceServer(args.host, args.port, args.db)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
