import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from db import DB

class Grapher:
    def __init__(self, item_limit=0):
        self.item_limit = item_limit

    def graph_cpu_usage(self, cpu_usage_values: list[float]) -> str:
        numvals = len(cpu_usage_values)
        plt.plot(range(1, numvals+1), cpu_usage_values)
        plt.ylim(0, 100)
        plt.ylabel("CPU Usage Percentage")
        #plt.show()
        plt.savefig('resource_graphs/cpu_usage.png')
        plt.clf()

    def graph_ram_usage(self, ram_usage_values: list[float], total_memory: float) -> str:
        numvals = len(ram_usage_values)
        total_memory = math.ceil(max(total_memory))
        plt.plot(range(1, numvals+1), ram_usage_values)
        plt.ylim(0, total_memory)
        plt.ylabel("RAM Usage")
        #plt.show()
        plt.savefig('resource_graphs/ram_usage.png')
        plt.clf()

    def graph_network_usage(self, network_usage_values: list[float]) -> str:
        numvals = len(network_usage_values)
        plt.plot(range(1, numvals+1), network_usage_values)
        plt.ylabel("Bytes Sent Over Network")
        #plt.show()
        plt.savefig('resource_graphs/network_usage.png')
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
