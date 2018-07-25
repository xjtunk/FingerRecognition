#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import time
import random
from collections import deque


plt.ion()

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
fig.set_size_inches(16, 4)
line, = ax.plot([1,2,3], [1,2,3])
ax.set_title('Test realtime plot')
ax.set_xlabel('Time')
ax.set_ylabel('CSI Amplitude')
cnt = 0
csi = []
# plt.show()
plt.grid(True)
winsize = 100
while True:
    csi.append(random.uniform(1,winsize))
    cnt += 1
    if cnt >= winsize:
        line.set_xdata([i for i in range(cnt - winsize, cnt)])
        line.set_ydata(csi[-winsize:])
        ax.set_xlim(cnt-winsize, cnt-1)
        ax.set_ylim(min(csi[-winsize:]), max(csi[-winsize:]))
        
        plt.pause(0.01)