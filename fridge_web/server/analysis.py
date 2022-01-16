import matplotlib.pyplot as plt
import numpy as np

from db import *

# Get some data
interval, n_points, sensor_id = '1 minutes', None, 0
query = '''
    SELECT t, d FROM (
        SELECT time_bucket(%s, time) AS t, avg(data) as d
        FROM fridge.data
        WHERE sensor_id = %s AND time < NOW() - INTERVAL '1 week'
        GROUP BY t
        ORDER BY t DESC LIMIT %s
    ) tt ORDER BY t ASC;
'''
values = (interval, sensor_id, n_points)
res = exec_query(query, values)

# Find min/max
from scipy.signal import savgol_filter

time, data = np.array(res)[:, :].T
time = np.array([(t - time[0]).total_seconds() for t in time], dtype=np.float64)
data = data.astype(np.float64)

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
print(f'Frequency: {f*10**4:.2f}e-4 Hz. Average low, high temperature: {lo:.2f} C, {hi:.2f} C')

# Plot
plt.plot(time, data_s, label='Data smoothed')
plt.plot(time, data, label='Data')

for p in peak_t:
    plt.axvline(p, color='gray')

plt.legend()
plt.grid()

plt.show()

