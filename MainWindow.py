# -*- coding: utf-8 -*
import struct
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QWidget, QPushButton, QLabel, QFrame, QPlainTextEdit
import numpy as np
from numpy import linspace
import pyqtgraph as pg
#from mem_top import mem_top
import cv2

from PositionWindow import PositionWindow

class MainWindow(QMainWindow):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.central_widget = QWidget()
        self.layout = QGridLayout(self.central_widget)

        # Widgets: Buttons, Sliders, ...
        self.camera_widget = CameraWidget(server)
        self.telem_widget = TelemWidget(server)
        self.control_widget = ControlWidget(server)
        self.mission_widget = MissionWidget(server)
        self.log_widget = LogWidget(server)

        # Timer for acquiring images at regular intervals
        self.acquisition_timer = QTimer()
        self.acquisition_timer.start(30)
        self.acquisition_timer.timeout.connect(self.update)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 6)
        self.layout.setRowStretch(1, 2)
        self.layout.setRowStretch(1, 1)
        self.layout.addWidget(self.camera_widget, 0, 0)
        self.layout.addWidget(self.telem_widget, 0, 1)
        self.layout.addWidget(self.mission_widget, 1, 0)
        self.layout.addWidget(self.control_widget, 1, 1)
        self.layout.addWidget(self.log_widget, 2, 0, 1, 2)

        self.setCentralWidget(self.central_widget)
    def update(self):
        self.camera_widget.update()

    def closeEvent(self, event):
        event.accept()
        self.server.close()
        self.close()

class LogWidget(QFrame):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.setFrameShape(QFrame.Box)
        #self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(3)
        self.layout = QGridLayout(self)
        self.log_widget = QPlainTextEdit()
        self.log_widget.setReadOnly(True)
        self.layout.addWidget(self.log_widget, 0, 0)
    def update(self):
        return

class ControlWidget(QFrame):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.setFrameShape(QFrame.Box)
        #self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(3)
        self.layout = QGridLayout(self)
        #define sub windows
        self.position_loop_window = PositionWindow(server)

        #define button widget
        self.arm_button = QPushButton("Arm", self)
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
        self.position_loop_button = QPushButton("位置环", self)
        self.velocity_loop_button = QPushButton("速度环", self)
        self.altitude_loop_button = QPushButton("姿态环", self)

        self.arm_button.clicked.connect(self.arm)
        self.takeoff_button.clicked.connect(self.takeoff)
        self.land_button.clicked.connect(self.land)
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

        self.layout.addWidget(self.arm_button, 0, 0, 1, 2)
        self.layout.addWidget(self.takeoff_button, 0, 2, 1, 2)
        self.layout.addWidget(self.land_button, 0, 4, 1, 2)
        self.layout.addWidget(self.up_button, 1, 0, 1, 1)
        self.layout.addWidget(self.down_button, 1, 1, 1, 1)
        self.layout.addWidget(self.forward_button, 2, 0, 1, 1)
        self.layout.addWidget(self.backward_button, 2, 1, 1, 1)
        self.layout.addWidget(self.left_button, 3, 0, 1, 1)
        self.layout.addWidget(self.right_button, 3, 1, 1, 1)
        self.layout.addWidget(self.yaw_pos_button, 1, 2, 1, 1)
        self.layout.addWidget(self.yaw_neg_button, 1, 3, 1, 1)
        self.layout.addWidget(self.thrust_button, 2, 2, 1, 1)
        self.layout.addWidget(self.position_loop_button, 1, 5, 1, 1)
        self.layout.addWidget(self.velocity_loop_button, 2, 5, 1, 1)
        self.layout.addWidget(self.altitude_loop_button, 3, 5, 1, 1)
        
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

class TelemWidget(QFrame):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.setFrameShape(QFrame.Box)
        #self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(3)
        self.layout = QGridLayout(self)

        #plot widget
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.map = self.plot_widget.addPlot()
        self.map.setXRange(-15, 15)
        self.map.setYRange(-15, 15)
        self.map.setAspectLocked()
        self.map.showGrid(x=1, y=1)
        self.map.showAxis("right")
        self.map.showAxis("top")
        self.map.setTitle("航迹俯视图(m)")
        self.map_curve = self.map.plot()

        self.layout.addWidget(self.plot_widget, 0, 0, 21, 21)

        #label widget
        self.flight_mode_label = QLabel("飞行模式:")
        self.battery_label = QLabel("电量:")
        self.rc_status_label = QLabel("遥控状态:")
        self.arm_status_label = QLabel("Armed:")
        self.in_air_label = QLabel("inAir:")

        self.height_label = QLabel("高度:00000m")
        self.roll_label = QLabel("roll:00000deg")
        self.pitch_label = QLabel("pitch:00000deg")
        self.yaw_label = QLabel("yaw:00000deg")
        self.velocity_label = QLabel("速度:00000m/s")
        self.velocity_north_label = QLabel("速度N:00000m/s")
        self.velocity_east_label = QLabel("速度E:00000m/s")
        self.velocity_down_label = QLabel("速度D:00000m/s")
        
        self.flight_mode_label.setFrameShape(QFrame.Box)
        self.battery_label.setFrameShape(QFrame.Box)
        self.rc_status_label.setFrameShape(QFrame.Box)
        self.arm_status_label.setFrameShape(QFrame.Box)
        self.in_air_label.setFrameShape(QFrame.Box)

        self.height_label.setFrameShape(QFrame.Box)
        self.roll_label.setFrameShape(QFrame.Box)
        self.pitch_label.setFrameShape(QFrame.Box)
        self.yaw_label.setFrameShape(QFrame.Box)
        self.velocity_label.setFrameShape(QFrame.Box)
        self.velocity_north_label.setFrameShape(QFrame.Box)
        self.velocity_east_label.setFrameShape(QFrame.Box)
        self.velocity_down_label.setFrameShape(QFrame.Box)

        self.layout.addWidget(self.flight_mode_label, 0, 21, 1, 2)
        self.layout.addWidget(self.battery_label, 1, 21, 1, 2)
        self.layout.addWidget(self.rc_status_label, 2, 21, 1, 2)
        self.layout.addWidget(self.arm_status_label, 3, 21, 1, 2)
        self.layout.addWidget(self.in_air_label, 4, 21, 1, 2)

        self.layout.addWidget(self.height_label, 10, 21, 1, 2)
        self.layout.addWidget(self.roll_label, 11, 21, 1, 2)
        self.layout.addWidget(self.pitch_label, 12, 21, 1, 2)
        self.layout.addWidget(self.yaw_label, 13, 21, 1, 2)
        self.layout.addWidget(self.velocity_label, 14, 21, 1, 2)
        self.layout.addWidget(self.velocity_north_label, 15, 21, 1, 2)
        self.layout.addWidget(self.velocity_east_label, 16, 21, 1, 2)
        self.layout.addWidget(self.velocity_down_label, 17, 21, 1, 2)

        #button widget
        self.clear_plot_button = QPushButton("清空图窗")
        self.start_log_button = QPushButton("保存日志", self)
        self.stop_log_button = QPushButton("停止", self)

        self.start_log_button.clicked.connect(self.start_log)
        self.stop_log_button.clicked.connect(self.stop_log)

        self.layout.addWidget(self.clear_plot_button, 18, 21, 1, 2)
        self.layout.addWidget(self.start_log_button, 19, 21, 1, 2)
        self.layout.addWidget(self.stop_log_button, 20, 21, 1, 2)
    def update(self):
        return
        #self.height_label.setText("123456")
        #if pose_data_queue != []:
        #    data = np.asarray(pose_data_queue, dtype=np.float)
        #    location_x = data[..., 0]
        #    location_y = data[..., 1]
        #    t = linspace(0, len(pose_data_queue) - 1, len(pose_data_queue))
        #    self.map_curve.setData(location_x, location_y)
    def start_log(self):
        buf = struct.pack('<?', True)
        self.server.send_msg(buf, 1, 6)
    def stop_log(self):
        buf = struct.pack('<?', False)
        self.server.send_msg(buf, 1, 6)

class CameraWidget(QFrame):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.setFrameShape(QFrame.Box)
        #self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(3)
        self.layout = QGridLayout(self)

        #define video widget
        self.camera_widget = pg.GraphicsLayoutWidget()
        self.camera_widget_box = self.camera_widget.addViewBox()
        self.camera_widget_box.setAspectLocked()
        self.camera_widget_item = pg.ImageItem()
        self.camera_widget_box.addItem(self.camera_widget_item)

        self.layout.addWidget(self.camera_widget, 0, 0, 21, 21)

        #define label widget
        self.target_label = QLabel("目标名称:")
        self.target_distance_label = QLabel("距离:")
        self.target_position_x_label = QLabel("位置x:")
        self.target_position_y_label = QLabel("位置y:")
        self.target_position_z_label = QLabel("位置z:")

        self.target_label.setFrameShape(QFrame.Box)
        self.target_distance_label.setFrameShape(QFrame.Box)
        self.target_position_x_label.setFrameShape(QFrame.Box)
        self.target_position_y_label.setFrameShape(QFrame.Box)
        self.target_position_z_label.setFrameShape(QFrame.Box)

        self.layout.addWidget(self.target_label, 0, 21, 1, 1)
        self.layout.addWidget(self.target_distance_label, 1, 21, 1, 1)
        self.layout.addWidget(self.target_position_x_label, 2, 21, 1, 1)
        self.layout.addWidget(self.target_position_y_label, 3, 21, 1, 1)
        self.layout.addWidget(self.target_position_z_label, 4, 21, 1, 1)
        
        #define button widget
        self.visual_feedback_button = QPushButton("视觉反馈", self)
        self.start_video_recording_button = QPushButton("录制视频", self)
        self.stop_video_recording_button = QPushButton("停止", self)

        self.start_video_recording_button.clicked.connect(self.start_video_recording)
        self.stop_video_recording_button.clicked.connect(self.stop_video_recording)
        self.layout.addWidget(self.visual_feedback_button, 18, 21, 1, 1)
        self.layout.addWidget(self.start_video_recording_button, 19, 21, 1, 1)
        self.layout.addWidget(self.stop_video_recording_button, 20, 21, 1, 1)
    def update(self):
        frame_queue = self.server.frame_queue.read()
        if frame_queue != []:
            frame = cv2.cvtColor(frame_queue[0], cv2.COLOR_BGR2RGB)
            frame = frame.transpose([1, 0, 2])
            frame = cv2.flip(frame, 1)
            self.camera_widget_item.setImage(frame)
    def start_video_recording(self):
        buffer = struct.pack('<?', True)
        self.server.send_msg(buffer, 1, 5)
    def stop_video_recording(self):
        buffer = struct.pack('<?', False)
        self.server.send_msg(buffer, 1, 5)

class MissionWidget(QFrame):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.setFrameShape(QFrame.Box)
        #self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(3)
        self.layout = QGridLayout(self)

        #define button widget
        self.start_button = QPushButton("任务开始", self)
        self.pause_button = QPushButton("暂停", self)
        self.continue_button = QPushButton("任务继续", self)
        self.reset_button = QPushButton("复位", self)
        self.config_button = QPushButton("修改配置文件", self)

        self.start_button.clicked.connect(self.start)
        self.pause_button.clicked.connect(self.pause)
        self.continue_button.clicked.connect(self._continue)
        self.reset_button.clicked.connect(self.reset)
        self.config_button.clicked.connect(self.config)

        self.layout.addWidget(self.start_button, 0, 0, 1, 1)
        self.layout.addWidget(self.pause_button, 1, 0, 1, 1)
        self.layout.addWidget(self.continue_button, 2, 0, 1, 1)
        self.layout.addWidget(self.reset_button, 3, 0, 1, 1)
        self.layout.addWidget(self.config_button, 0, 1, 1, 1)
    def update(self):
        return
    def start(self):
        return
    def pause(self):
        return
    def _continue(self):
        return
    def reset(self):
        return
    def config(self):
        return
