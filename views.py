# -*- coding: utf-8 -*
import struct
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QWidget, QPushButton, QLabel
import numpy as np
from numpy import linspace
import pyqtgraph as pg
#from mem_top import mem_top
import cv2

class PositionWidget(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        # Widgets layout
        self.north = self.addPlot(row=0, col=0, rowspan=1, colspan=1)
        self.east = self.addPlot(row=1, col=0, rowspan=1, colspan=1)
        self.down = self.addPlot(row=2, col=0, rowspan=1, colspan=1)

        self.north.setLabel('left', text="North(m)")
        self.east.setLabel('left', text="East(m)")
        self.down.setLabel('left', text='Down(m)')

        self.north_curve = self.north.plot()
        self.east_curve = self.east.plot()
        self.down_curve = self.down.plot()
    def update(self, position_queue):
        if position_queue != []:
            data = np.asarray(position_queue, dtype=np.float)
            north = data[..., 0]
            north_t = data[..., 1]
            east = data[..., 2]
            east_t = data[..., 3]
            down = data[..., 4]
            down_t = data[..., 5]

            self.north_curve.setData(north_t, north)
            self.east_curve.setData(east_t, east)
            self.down_curve.setData(down_t, down)     

class PositionWindow(QMainWindow):
    def __init__(self, server):
        super().__init__()
        self.udp_server = server
        self.central_widget = QWidget()
        self.position_widget = PositionWidget()

        self.acquisition_timer = QTimer()
        self.acquisition_timer.start(30)
        self.acquisition_timer.timeout.connect(self.update)

        self.layout = QGridLayout(self.central_widget)
        self.layout.addWidget(self.position_widget, 0, 0)

        self.setCentralWidget(self.central_widget)
    def update(self):
        position_queue = self.udp_server.position_queue.read()
        self.position_widget.update(position_queue)

class VideoWidget(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        self.video_widget_box = self.addViewBox()
        self.video_widget_box.setAspectLocked()
        self.video_widget_item = pg.ImageItem()
        self.video_widget_box.addItem(self.video_widget_item)
    def update(self, frame_queue):
        if frame_queue != []:
            frame = cv2.cvtColor(frame_queue[0], cv2.COLOR_BGR2RGB)
            frame = frame.transpose([1, 0, 2])
            frame = cv2.flip(frame, 1)
            self.video_widget_item.setImage(frame)

class StatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Widgets: Buttons, Sliders, ...
        self.video_recording_label = QLabel()
        # Widgets layout
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.video_recording_label, 0, 0)
    def update(self, state_param_queue):
        if state_param_queue == []:
            return
        param = state_param_queue[0]
        self.video_recording_label.setText("录制开启: " + str(param[1]))

class PoseWidget(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        # Widgets layout
        self.location = self.addPlot()
        self.height = self.addPlot()

        self.location.setXRange(-15, 15)
        self.location.setYRange(-15, 15)
        self.location.setAspectLocked()
        self.height.setXRange(0, 200)

        self.location.setLabel('top', text="航迹俯视图(m)")
        self.height.setLabel('top', text="高度(m)")

        self.location_curve = self.location.plot()
        self.height_curve = self.height.plot()

    def update(self, pose_data_queue):
        if pose_data_queue != []:
            data = np.asarray(pose_data_queue, dtype=np.float)
            location_x = data[..., 0]
            location_y = data[..., 1]
            height = data[..., 2]
            t = linspace(0, len(pose_data_queue) - 1, len(pose_data_queue))
            self.location_curve.setData(location_x, location_y)
            self.height_curve.setData(t, height)

class ControlWidget(QWidget):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.position_loop_window = PositionWindow(server)

        # Widgets: Buttons, Sliders, ...
        self.arm_button = QPushButton("准备", self)
        self.takeoff_button = QPushButton("起飞", self)
        self.land_button = QPushButton("降落", self)

        self.up_button = QPushButton("UP", self)
        self.down_button = QPushButton("DOWN", self)
        self.forward_button = QPushButton("FORWARD", self)
        self.backward_button = QPushButton("BACKWARD", self)
        self.left_button = QPushButton("LEFT", self)
        self.right_button = QPushButton("RIGHT", self)
        self.yaw_pos_button = QPushButton("YAW+", self)
        self.yaw_neg_button = QPushButton("YAW-", self)
        self.thrust_button = QPushButton("THRUST", self)

        self.start_video_recording_button = QPushButton("录制视频", self)
        self.stop_video_recording_button = QPushButton("停止", self)

        self.start_log_button = QPushButton("保存数据", self)
        self.stop_log_button = QPushButton("停止", self)


        self.position_loop_button = QPushButton("位置环", self)
        self.velocity_loop_button = QPushButton("速度环", self)
        self.altitude_loop_button = QPushButton("姿态环", self)

        # Signals
        self.arm_button.clicked.connect(self.arm)
        self.takeoff_button.clicked.connect(self.takeoff)
        self.land_button.clicked.connect(self.land)
        self.start_video_recording_button.clicked.connect(self.start_video_recording)
        self.stop_video_recording_button.clicked.connect(self.stop_video_recording)

        self.start_log_button.clicked.connect(self.start_log)
        self.stop_log_button.clicked.connect(self.stop_log)

        self.up_button.clicked.connect(self.up)
        self.down_button.clicked.connect(self.down)
        self.forward_button.clicked.connect(self.forward)
        self.backward_button.clicked.connect(self.backward)
        self.left_button.clicked.connect(self.left)
        self.right_button.clicked.connect(self.right)
        self.yaw_pos_button.clicked.connect(self.yaw_pos)
        self.yaw_neg_button.clicked.connect(self.yaw_neg)
        self.thrust_button.clicked.connect(self.thrust)


        self.position_loop_button.clicked.connect(self.position_loop_show)

        # Widgets layout
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.arm_button, 0, 0, 1, 2)
        self.layout.addWidget(self.takeoff_button, 0, 2, 1, 2)
        self.layout.addWidget(self.land_button, 0, 4, 1, 2)

        self.layout.addWidget(self.start_video_recording_button, 1, 0, 1, 1)
        self.layout.addWidget(self.stop_video_recording_button, 1, 1, 1, 1)
        self.layout.addWidget(self.start_log_button, 2, 0, 1, 1)
        self.layout.addWidget(self.stop_log_button, 2, 1, 1, 1)

        self.layout.addWidget(self.up_button, 1, 2, 1, 1)
        self.layout.addWidget(self.down_button, 1, 3, 1, 1)
        self.layout.addWidget(self.forward_button, 2, 2, 1, 1)
        self.layout.addWidget(self.backward_button, 2, 3, 1, 1)
        self.layout.addWidget(self.left_button, 3, 2, 1, 1)
        self.layout.addWidget(self.right_button, 3, 3, 1, 1)
        self.layout.addWidget(self.yaw_pos_button, 4, 2, 1, 1)
        self.layout.addWidget(self.yaw_neg_button, 4, 3, 1, 1)
        self.layout.addWidget(self.thrust_button, 4, 0, 1, 1)

        self.layout.addWidget(self.position_loop_button, 1, 4, 1, 2)
        self.layout.addWidget(self.velocity_loop_button, 2, 4, 1, 2)
        self.layout.addWidget(self.altitude_loop_button, 3, 4, 1, 2)
    def arm(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 0)
    def takeoff(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 1)
    def land(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 2)
    def up(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 3)
    def down(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 4)
    def start_video_recording(self):
        buffer = struct.pack('<?', True)
        self.server.send_msg(buffer, 1, 5)
    def stop_video_recording(self):
        buffer = struct.pack('<?', False)
        self.server.send_msg(buffer, 1, 5)
    def start_log(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 6)
    def stop_log(self):
        buf = struct.pack('<?', False)
        self.server.send_msg(buf, 1, 6)
    def forward(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 7)
    def backward(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 8)
    def left(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 9)
    def right(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 10)
    def yaw_pos(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 11)
    def yaw_neg(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 12)
    def thrust(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 13)
    def position_loop_show(self):
        self.position_loop_window.show()


class MainWindow(QMainWindow):
    def __init__(self, udp_server, tcp_server):
        super().__init__()
        self.udp_server = udp_server
        self.tcp_server = tcp_server
        self.central_widget = QWidget()

        # Widgets: Buttons, Sliders, ...
        self.video_widget = VideoWidget()
        self.pose_widget = PoseWidget()
        self.control_widget = ControlWidget(tcp_server)
        self.status_widget = StatusWidget()

        # Timer for acquiring images at regular intervals
        self.acquisition_timer = QTimer()
        self.acquisition_timer.start(30)
        self.acquisition_timer.timeout.connect(self.update)

        self.layout = QGridLayout(self.central_widget)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 2)
        self.layout.setRowStretch(1, 1)
        self.layout.addWidget(self.video_widget, 0, 0)
        self.layout.addWidget(self.pose_widget, 0, 1)
        self.layout.addWidget(self.status_widget, 1, 0)
        self.layout.addWidget(self.control_widget, 1, 1)

        self.setCentralWidget(self.central_widget)
    def update(self):
        #print( mem_top())
        frame_queue = self.udp_server.frame_queue.read()
        self.video_widget.update(frame_queue)

        #pose_data_queue = self.udp_server.pose_data_queue.read()
        #self.pose_widget.update(pose_data_queue)

        status_queue = self.udp_server.state_param_queue.read()
        self.status_widget.update(status_queue)

    def closeEvent(self, event):
        event.accept()
        self.udp_server.close()
        self.tcp_server.close()
        self.close()
