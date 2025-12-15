import matplotlib.pyplot as plt
import pandas as pd
from db import DB

class Grapher:
    def graph_cpu_usage(self, cpu_usage_values: list[float]) -> str:
        plt.plot(cpu_usage_values)
        plt.ylabel("CPU Usage Percentage")
        plt.show()
        plt.savefig('resource_graphs/cpu_usage.png')
        plt.clf()

    def graph_ram_usage(self, ram_usage_values: list[float], total_memory: float) -> str:
        plt.plot(ram_usage_values)
        plt.ylabel("RAM Usage")
        plt.show()
        plt.clf()


if __name__ == '__main__':
    g = Grapher()
    db = DB()
    client_data = db.get_client_data('10.245.81.94')

    cpu_data = db.extract_field_from_data('cpu_usage', client_data)
    #print(cpu_data)
    #g.graph_cpu_usage(cpu_data)

    ram_data = db.extract_field_from_data('memory_usage', client_data)
    total_memory = db.extract_field_from_data('total_memory', client_data)
    print(total_memory)
    #print(ram_data)
    g.graph_ram_usage(ram_data, total_memory)
