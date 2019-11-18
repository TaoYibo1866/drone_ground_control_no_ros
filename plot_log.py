import csv
from sys import argv
import numpy as np
import matplotlib.pyplot as plt
from math import sin, cos

path = argv[1]
position_ned = []
velocity_body = []
euler_angle = []
input_attitude = []
reference_down = []
target = []
control_status = []
pos_xy_err = []

with open(path) as f:
    csv_file = csv.reader(f)
    for row in csv_file:
        if row[0] == "PositionNED":
            position_ned.append(row[1:])
        elif row[0] == "VelocityBody":
            velocity_body.append(row[1:])
        elif row[0] == "EulerAngle":
            euler_angle.append(row[1:])
        elif row[0] == "InputAttitude":
            input_attitude.append(row[1:])
        elif row[0] == "ReferenceDown":
            reference_down.append(row[1:])
        elif row[0] == "Target":
            target.append(row[1:])
        elif row[0] == "ControlStatus":
            control_status.append(row[1:])
        elif row[0] == 'PosXYErr':
            pos_xy_err.append(row[1:])
   
if pos_xy_err != []:
    err = np.asarray(pos_xy_err, np.float32)
    err_t = err[:,0] / 1000
    err_x = err[:,1]
    err_y = err[:,2]
    fig5, (ax1, ax2) = plt.subplots(2, 1)
    fig5.subplots_adjust(hspace=0.1)
    ax1.plot(err_t, err_x)
    ax2.plot(err_t, err_y)
    ax1.grid(True)
    ax2.grid(True)
    fig5.suptitle('ERR')
    ax1.set_ylabel("X/m")
    ax2.set_ylabel("Y/m")
    fig5.show()

if control_status != []:
    control_status = np.asarray(control_status, np.float32)
    c_t = control_status[:,0] / 1000
    c = control_status[:,1]
    fig9, (ax1, ax2) = plt.subplots(2, 1)
    fig9.subplots_adjust(hspace=0.1)
    ax1.plot(c_t, c)
    ax1.grid(True)
    fig9.suptitle("ControlStatus")
    fig9.show()

if position_ned != []:
    position_ned = np.asarray(position_ned, np.float32)
    position_d = -1 * position_ned[:,3]
    position_n = position_ned[:,1]
    position_e = position_ned[:,2]
    position_t = position_ned[:,0] / 1000
    fig1, (ax1, ax2, ax3) = plt.subplots(3, 1)
    fig1.subplots_adjust(hspace=0.1)
    ax1.plot(position_t, position_n)
    ax2.plot(position_t, position_e)
    ax3.plot(position_t, position_d)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    fig1.suptitle('PositionNED')
    ax1.set_ylabel("N/m")
    ax2.set_ylabel("E/m")
    ax3.set_ylabel("-D/m")
    fig1.show()

if target != []:
    target = np.asarray(target, np.float32)
    target_t = target[:,0] / 1000
    target_d = target[:, 2]
    target_x = target[:, 3]
    target_y = target[:, 4]
    target_z = target[:, 5]
    target_c = target[:, 6]
    target_t = target_t[target_c > 0]
    target_d = target_d[target_c > 0]
    target_x = target_x[target_c > 0]
    target_y = target_y[target_c > 0]
    target_z = target_z[target_c > 0]
    target_c = target_c[target_c > 0]

    fig2, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
    fig2.subplots_adjust(hspace=0.1)
    ax1.scatter(target_t, target_d, marker='x')
    ax2.scatter(target_t, target_x, marker='x')
    ax3.scatter(target_t, target_y, marker='x')
    ax4.scatter(target_t, target_z, marker='x')

    ax1.set_ylabel("distance/m")
    ax2.set_ylabel("x/m")
    ax3.set_ylabel("y/m")
    ax4.set_ylabel("z/m")
    fig2.show()

if euler_angle != []:
    euler_angle = np.asarray(euler_angle, np.float32)
    roll = euler_angle[:,1]
    pitch = euler_angle[:,2]
    yaw = euler_angle[:,3]
    euler_angle_t = euler_angle[:,0] / 1000
    
    fig4, (ax1, ax2, ax3) = plt.subplots(3, 1)
    fig4.subplots_adjust(hspace=0.1)
    ax1.plot(euler_angle_t, roll)
    ax2.plot(euler_angle_t, pitch)
    ax3.plot(euler_angle_t, yaw)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    fig4.suptitle('Attitude')
    ax1.set_ylabel("roll/deg")
    ax2.set_ylabel("pitch/deg")
    ax3.set_ylabel("yaw/deg")
    fig4.show()

if input_attitude != []:
    input_attitude = np.asarray(input_attitude, np.float32)
    input_roll = input_attitude[:,1]
    input_pitch = input_attitude[:,2]
    input_yaw = input_attitude[:,3]
    input_thrust = input_attitude[:,4]
    input_t = input_attitude[:,0] / 1000

    fig3, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
    fig3.subplots_adjust(hspace=0.1)
    ax1.plot(input_t, input_roll)
    ax2.plot(input_t, input_pitch)
    ax3.plot(input_t, input_yaw)
    ax4.plot(input_t, input_thrust)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax4.grid(True)
    fig3.suptitle('InputAttitude')
    ax1.set_ylabel("roll/deg")
    ax2.set_ylabel("pitch/deg")
    ax3.set_ylabel("yaw/deg")
    ax4.set_ylabel("thrust")
    fig3.show()

if reference_down != []:
    reference = np.asarray(reference_down, np.float32)
    reference_t = reference[:,0] / 1000
    reference_d = -1 * reference[:,1]
    fig6, ax = plt.subplots(1, 1)
    fig6.subplots_adjust(hspace=0.1)
    ax.plot(reference_t, reference_d)
    ax.grid(True)
    fig6.suptitle('ReferenceDown')
    ax.set_ylabel("-pos_sp_z/m")
    fig6.show()
    
if velocity_body != []:
    velocity = np.asarray(velocity_body, np.float32)
    velocity_t = velocity[:,0] / 1000
    velocity_x = velocity[:,1]
    velocity_y = velocity[:,2]
    velocity_z = velocity[:,3]
    fig7, (ax1, ax2, ax3) = plt.subplots(3, 1)
    fig7.subplots_adjust(hspace=0.1)
    ax1.plot(velocity_t, velocity_x)
    ax1.grid(True)
    ax2.plot(velocity_t, velocity_y)
    ax2.grid(True)
    ax3.plot(velocity_t, velocity_z)
    ax3.grid(True)
    fig7.suptitle('VelocityBody')
    fig7.show()

# fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
# fig.subplots_adjust(hspace=0.1)
# ax1.plot(position_t, position_d, target_t, target_y)
# ax1.set_xlim(input_t[0], input_t[-1])
# ax1.grid(True)

# ax2.plot(position_t, position_e, marker='x')
# ax2.set_xlim(input_t[0], input_t[-1])
# ax2.grid(True)

# ax3.plot(input_t, input_roll, marker='x')
# ax3.set_xlim(input_t[0], input_t[-1])
# ax3.grid(True)

# ax4.plot(input_t, input_pitch, marker='x')
# ax4.set_xlim(input_t[0], input_t[-1])
# ax4.grid(True)

plt.show()
