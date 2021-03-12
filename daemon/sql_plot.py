from db_helpers import execute_query

import numpy as np


def plot_all():
    query = '''SELECT time, data FROM fridge_data WHERE sensor_id = 0;'''
    data = execute_query(query)

    time, temperature = [d[0] for d in data], [d[1] for d in data]
    plt.plot(time, temperature)


if __name__ == '__main__':
    plot_all()
