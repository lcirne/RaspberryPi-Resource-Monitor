import matplotlib.pyplot as plt
import json

def horizontal_bar_chart(json_string):
    system_usage_dict = json.loads(json_string)
    print(system_usage_dict)
    print(system_usage_dict['name'])


if __name__=='__main__':
    horizontal_bar_chart('{"name": "Alice", "age": 30, "city": "New York"}')


