from scipy.signal import savgol_filter
import numpy as np
from datetime import datetime, timedelta

from db import *

# Retrieve data from some point to now
def get_data(interval='1 minutes', n_points=None, sensor_id=0, t_back='1 month'):
    query = '''
        SELECT t, d FROM (
            SELECT time_bucket(%s, time) AS t, avg(data) as d
            FROM fridge.data
            WHERE sensor_id = %s AND time > NOW() - INTERVAL %s
            GROUP BY t
            ORDER BY t DESC LIMIT %s
        ) tt ORDER BY t ASC;
    '''
    values = (interval, sensor_id, t_back, n_points)
    res = exec_query(query, values)

    time, data = np.array(res).T
    return time, data.astype(np.float64)

def diff(d):
    return np.r_[0, np.diff(d)]

def print_dt(dt):
    return dt.strftime("%H:%M")

# Extract some relevant info
def get_sig_info(time, data):
    # Convert to relative time
    t0 = time[0]
    time = np.array([(t - t0).seconds for t in time], dtype=np.float64)

    # Smooth
    data_s = savgol_filter(data, 21, 3)
    data_d = diff(np.sign(diff(data_s)))

    idxs = np.where(np.abs(data_d) == 2)[0] - 1 # Difference switch
    peak_t, peak_d = time[idxs], data[idxs]

    # Basically same as non maxima suppression for bboxes -> greedy algorithm
    def nms(peak_t, peak_d, dt=30*60):
        peak_t_o, peak_d_o = [], []
        for i in range(len(peak_t)):
            window = np.where(np.abs(peak_t - peak_t[i]) < dt)[0]
            if len(window) >= 1:
                i = window[np.argmax(peak_d[window])]

            peak_t_o.append(peak_t[i])
            peak_d_o.append(peak_d[i])

        return np.array(peak_t_o), np.array(peak_d_o)

    # Run nms iteratively
    peak_t_prev = peak_t - 1 # Slightly different initially
    while not np.all(peak_t == peak_t_prev):
        peak_t_prev = np.copy(peak_t)
        peak_t, peak_d = nms(peak_t, peak_d)

    # Get data at peak times
    tops, bottoms = peak_d[peak_d > peak_d.mean()], peak_d[peak_d < peak_d.mean()]
    hi, lo = tops.mean(), bottoms.mean()

    peak_t_abs = [timedelta(seconds=t) + t0 for t in peak_t]
    return hi, lo, peak_d, peak_t_abs, peak_t

# Control input to disable when sleeping
def get_command(time, data, t_sleep='23:59'):
    # Sleep time in absolute terms
    t_sleep = datetime.strptime(t_sleep, "%H:%M")
    t_sleep = datetime.today().replace(hour=t_sleep.hour, minute=t_sleep.minute, second=0, microsecond=0)

    hi, lo, peak_d, peak_t, peak_t_rel = get_sig_info(time, data)

    # Calculate slopes to compute predicted on times
    last_peak_d, last_peak_t = peak_d[-1], peak_t[-1]
    slope = 1 if abs(last_peak_d - lo) < abs(last_peak_d - hi) else -1 # Rising/falling

    # Turns out that time is a much better indicator than temperature for this fridge's control...
    dt = np.median(np.diff(peak_t_rel))

    # Compute closest peak BEFORE sleep
    next_peaks = last_peak_t + np.arange(1, 20)*timedelta(seconds=dt)
    idxs = np.where(((t_sleep - next_peaks) > timedelta(seconds=0)))[0]
    idxs = idxs[(idxs + max(slope, 0)) % 2 == 0] # Only find minima

    rel_peak = next_peaks[idxs[-1]]
    delay = (t_sleep - rel_peak).seconds

    # This makes the assumption that frequency is around 2 hours (i.e. max delay is under 2 hours)
    command = ""
    if delay > dt:
        t_turn_off = dt/2 # Maximum possible turn off

        f = rel_peak - timedelta(seconds=2*dt + t_turn_off)
        command += f"Turn on/off multiple times, check back later. First turn off for {t_turn_off/60:.0f} minutes at {print_dt(f)}. "

        delay -= dt

    t_turn_off = delay/2
    f = rel_peak - timedelta(seconds=dt - t_turn_off)
    command += f"Turn off for {t_turn_off/60:.0f} minutes at {print_dt(f)}."

    return command

if __name__ == '__main__':
    time, data = get_data(t_back='12 hours', interval='2 minutes')

    command = get_command(time, data)
    print(command)

    # Plot
    import matplotlib.pyplot as plt
    plt.plot(time, data, label='Data')

    hi, lo, peak_d, peak_t, peak_t_rel = get_sig_info(time, data)
    for p in peak_t:
        plt.axvline(p, color='gray')

    plt.legend()
    plt.grid()

    plt.show()

