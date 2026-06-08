import argparse
import socket
import time

from monitor import Monitor


DEFAULT_PORT = 4000
DEFAULT_INTERVAL = 1.0


def stream_metrics(host: str, port: int, interval: float) -> None:
    monitor = Monitor()

    while True:
        try:
            with socket.create_connection((host, port), timeout=10) as client:
                client.settimeout(10)
                print(f"Connected to {host}:{port}")
                while True:
                    message = monitor.get_system_resource_usage() + "\n"
                    client.sendall(message.encode("utf-8"))
                    time.sleep(interval)
        except (ConnectionError, OSError, TimeoutError) as exc:
            print(f"Connection unavailable ({exc}); retrying in 3 seconds")
            time.sleep(3)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stream this machine's resource metrics to the Raspberry Pi monitor."
    )
    parser.add_argument("host", help="Server IP address or hostname")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        stream_metrics(args.host, args.port, args.interval)
    except KeyboardInterrupt:
        print("Client stopped")


if __name__ == "__main__":
    main()
