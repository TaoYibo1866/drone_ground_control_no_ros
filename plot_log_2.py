import csv
from sys import argv
import numpy as np
import matplotlib.pyplot as plt
from math import sin, cos

path = argv[1]
position = []
with open(path) as f:
    csv_file = csv.reader(f)
    for row in csv_file:
        if row[0] == "Target":
            position.append(row[1:])
            
position = np.asarray(position, np.float32)
position_x = position[:,4]
position_y = position[:,2]
position_z = position[:,3]
position_conf = position[:,5]
position_t = position[:,6] / 1000

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
fig.subplots_adjust(hspace=0.1)
ax1.plot(position_t, position_conf, marker='x')
ax1.grid(True)

ax2.plot(position_t, position_x, marker='x')
ax2.grid(True)

ax3.plot(position_t, position_y, marker='x')
ax3.grid(True)

ax4.plot(position_t, position_z, marker='x')
ax4.grid(True)

plt.show()
