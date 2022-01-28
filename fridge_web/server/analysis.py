from scipy.signal import savgol_filter
import numpy as np
from datetime import datetime

from db import *

# Retrieve data from some point to now
def get_data(interval='1 minutes', t_back='2 days', sensor_id=0):
    query = '''
        SELECT t, d FROM (
            SELECT time_bucket(%s, time) AS t, avg(data) as d
            FROM fridge.data
            WHERE sensor_id = %s AND time > NOW() - INTERVAL %s
            GROUP BY t
            ORDER BY t DESC
        ) tt ORDER BY t ASC;
    '''
    values = (interval, sensor_id, t_back)
    res = exec_query(query, values)

    time, data = np.array(res).T
    return time, data.astype(np.float64)

# Extract some relevant info
def get_sig_info(time, data):
    # Convert to relative time
    time = np.array([(t - time[0]).total_seconds() for t in time], dtype=np.float64)

    # Smooth
    data_s = savgol_filter(data, 21, 3)

    diff = lambda d: np.r_[0, np.diff(d)]
    data_d = diff(np.sign(diff(data_s)))

    idxs = np.where(np.abs(data_d) == 2)[0] - 1 # Difference switch
    peak_t, peak_d = time[idxs], data[idxs]

    peak_t_d = diff(peak_t)
    idxs = np.where(peak_t_d > 1800) # Keep only peaks with min half hour between them
    peak_t, dt = peak_t[idxs], peak_t_d[idxs]

    # Frequency from average time diff
    f = 1/dt.mean()

    # Get data at peak times
    peak_d = peak_d[idxs]
    tops, bottoms = peak_d[peak_d > peak_d.mean()], peak_d[peak_d < peak_d.mean()]

    hi, lo = tops.mean(), bottoms.mean()
    return f, hi, lo

if __name__ == '__main__':
    time, data = get_data(t_back='2 days')
    print(get_sig_info(time, data))

    # Plot
    import matplotlib.pyplot as plt
    plt.plot(time, data, label='Data')

    plt.legend()
    plt.grid()

    plt.show()

