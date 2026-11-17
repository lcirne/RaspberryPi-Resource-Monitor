import json
import socket
import time

import psutil

class Monitor:
    def __init__(self):
        self.last_network = psutil.net_io_counters()
        self.last_network_time = time.time()

    def get_system_resource_usage(self) -> str:
        return json.dumps(self.get_system_resource_snapshot())

    def get_system_resource_snapshot(self) -> dict:
        cpu_usage = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        network = psutil.net_io_counters()
        now = time.time()

        elapsed = max(now - self.last_network_time, 0.001)
        net_sent_rate = (network.bytes_sent - self.last_network.bytes_sent) / elapsed
        net_recv_rate = (network.bytes_recv - self.last_network.bytes_recv) / elapsed
        self.last_network = network
        self.last_network_time = now

        ip_type, current_ip = self.get_primary_ip()

        return {
            "observed_at": now,
            "client_ip": current_ip,
            "client_hostname": socket.gethostname(),
            "ip_type": ip_type,
            "cpu_usage": cpu_usage,
            "memory_usage": memory.used / (1024**3),
            "total_memory": memory.total / (1024**3),
            "disk_usage": disk.used / (1024**3),
            "total_disk": disk.total / (1024**3),
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "net_sent_rate": max(net_sent_rate, 0),
            "net_recv_rate": max(net_recv_rate, 0),
        }

    def get_primary_ip(self) -> tuple[str, str]:
        for interface_name, address in self.get_local_ips().items():
            if not address.startswith("127."):
                return interface_name, address
        return "local", "127.0.0.1"

    def get_local_ips(self) -> dict[str, str]:
        ip_addresses = {}
        interfaces = psutil.net_if_addrs()
        for interface_name, addresses in interfaces.items():
            for address in addresses:
                if address.family == socket.AF_INET:
                    ip_addresses[interface_name] = address.address
        return ip_addresses


if __name__ == "__main__":
    monitor = Monitor()
    print(json.dumps(monitor.get_system_resource_snapshot(), indent=2))
