import psutil
import time
import socket
import json

class Monitor:
    def __init__(self):
        self.system_resource_usage = {}

    def get_system_resource_usage(self):
        """Monitors and prints system resource usage."""

        # CPU Usage
        cpu_usage = psutil.cpu_percent(interval=1)

        # Memory Usage
        memory = psutil.virtual_memory()
        memory_used_gbs = memory.used / (1024**3)

        # Total memory
        total_memory = memory.total / (1024**3)

        # Disk Usage (for the root partition, modify as needed for other partitions)
        disk = psutil.disk_usage('/')
        disk_usage = disk.used / (1024**3)

        # Network Usage (bytes sent and received)
        network = psutil.net_io_counters()
        bytes_sent = network.bytes_sent
        bytes_recv = network.bytes_recv

        # Name of client
        client_hostname = socket.gethostname()

        # Current IP
        ips = self.get_local_ips() # Dictionary of ip address types and addresses
        if 'en0' in ips:
            en0 = ips['en0']
            current_ip = ('en0', en0)
        elif 'wlp4s0' in ips:
            wlp4s0 = ips['wlp4s0']
            current_ip = ('wlp4s0', wlp4s0)
        else:
            local_ip = ips['lo']
            current_ip = ('local', local_ip)

        # Load items into dictionary and serialize as json
        self.system_resource_usage['client_ip'] = current_ip[1]
        self.system_resource_usage['client_hostname'] = client_hostname
        self.system_resource_usage['ip_type'] = current_ip[0]
        self.system_resource_usage['cpu_usage'] = cpu_usage
        self.system_resource_usage['memory_usage'] = memory_used_gbs
        self.system_resource_usage['total_memory'] = total_memory
        self.system_resource_usage['bytes_sent'] = bytes_sent
        self.system_resource_usage['bytes_recv'] = bytes_recv
        self.system_resource_usage['disk_usage'] = disk_usage
        info_json = json.dumps(self.system_resource_usage, indent=4)
        return info_json


# Function to parse psutil.net_if_addrs() output for 'address' variable
    def get_local_ips(self):
        ip_addresses = {}
        interfaces = psutil.net_if_addrs()
        for interface_name, addresses in interfaces.items():
            for address in addresses:
                if address.family == socket.AF_INET:
                    ip_addresses[interface_name] = address.address
        return ip_addresses


if __name__ == '__main__':
    system_usage = get_system_resource_usage()
    print(system_usage)
