import csv
from sys import argv
import numpy as np
import matplotlib.pyplot as plt
from math import sin, cos

path = argv[1]
position_ned = []
velocity_ned = []
euler_angle = []
input_attitude = []
reference = []
target = []
control_status = []

with open(path) as f:
    csv_file = csv.reader(f)
    for row in csv_file:
        if row[0] == "PositionNED":
            position_ned.append(row[1:])
        elif row[0] == "VelocityNED":
            velocity_ned.append(row[1:])
        elif row[0] == "EulerAngle":
            euler_angle.append(row[1:])
        elif row[0] == "InputAttitude":
            input_attitude.append(row[1:])
        elif row[0] == "Reference":
            reference.append(row[1:])
        elif row[0] == "Target":
            target.append(row[1:])
        elif row[0] == "ControlStatus":
            control_status.append(row[1:])

print(control_status)
position_ned = np.asarray(position_ned, np.float32)
position_d = -1 * position_ned[:,2]
position_n = position_ned[:,0]
position_e = position_ned[:,1]
position_t = position_ned[:,3] / 1000

yaw = 3.14159 * 0 / 180
position_n_e = position_ned[:, 0:2]
R = np.asarray([[cos(yaw), -sin(yaw)], [sin(yaw), cos(yaw)]], np.float32)
position_n_e = np.dot(position_n_e, R)
position_n = position_n_e[:,0]
position_e = position_n_e[:,1]

target = np.asarray(target, np.float32)
target_t = target[:,-1] / 1000
target_y = target[:, 3]


euler_angle = np.asarray(euler_angle, np.float32)
roll = euler_angle[:,0]
pitch = euler_angle[:,1]
yaw = euler_angle[:,2]
euler_angle_t = euler_angle[:,3] / 1000

input_attitude = np.asarray(input_attitude, np.float32)
input_roll = input_attitude[:,0]
input_pitch = input_attitude[:,1]
input_yaw = input_attitude[:,2]
input_thrust = input_attitude[:,3]
input_t = input_attitude[:,4] / 1000

reference = np.asarray(reference, np.float32)
reference_t = reference[:,1] / 1000
reference_d = -1 * reference[:,0]

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
fig.subplots_adjust(hspace=0.1)
ax1.plot(position_t, position_d, target_t, target_y)
ax1.set_xlim(input_t[0], input_t[-1])
ax1.grid(True)

ax2.plot(position_t, position_e, marker='x')
ax2.set_xlim(input_t[0], input_t[-1])
ax2.grid(True)

ax3.plot(input_t, input_roll, marker='x')
ax3.set_xlim(input_t[0], input_t[-1])
ax3.grid(True)

ax4.plot(input_t, input_pitch, marker='x')
ax4.set_xlim(input_t[0], input_t[-1])
ax4.grid(True)

plt.show()
