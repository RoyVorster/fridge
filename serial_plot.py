import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import serial
import re

n_plot = 20

ydat = [0.]*n_plot 
xdat = list(range(0, n_plot))

serial_in = serial.Serial('/dev/ttyUSB0', 115200)

fig, ax = plt.subplots()
ax.axis([0, n_plot - 1, 0, 40])
line, = ax.plot([])

def get_data():
    while True:
        try:
            l = serial_in.readline().decode('utf-8')

            ms = re.match(r'Temperature: (?P<temperature>([0-9]*[.])?([0-9]*))', l)
            data = float(ms['temperature']) if ms is not None else 0.
        except:
            data = 0.

        yield data

def anim(data):
    global ydat

    if data != 0.:
        ydat = [data] + ydat[:-1]

    line.set_data(xdat, ydat)
    return line,

if __name__ == '__main__':
    a = animation.FuncAnimation(fig, anim, get_data, interval=1, blit=True)
    plt.show()

