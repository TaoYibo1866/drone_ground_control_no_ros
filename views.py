# -*- coding: utf-8 -*
import struct
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QWidget, QPushButton, QLabel
import numpy as np
from numpy import linspace
import pyqtgraph as pg
#from mem_top import mem_top
import cv2

class VideoWidget(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        self.video_widget_box = self.addViewBox()
        self.video_widget_box.setAspectLocked()
        self.video_widget_Item = pg.ImageItem()
        self.video_widget_box.addItem(self.video_widget_Item)
    def update(self, frame_queue):
        if frame_queue != []:
            frame = cv2.cvtColor(frame_queue[0], cv2.COLOR_BGR2RGB)
            frame = frame.transpose([1, 0, 2])
            frame = cv2.flip(frame, 1)
            self.video_widget_Item.setImage(frame)

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
        self.location = self.addPlot(row=0, col=0, rowspan=3, colspan=1)
        self.height = self.addPlot(row=3, col=0, rowspan=1, colspan=1)
        self.v_x = self.addPlot(row=0, col=1, rowspan=1, colspan=1)
        self.v_y = self.addPlot(row=1, col=1, rowspan=1, colspan=1)
        self.v_z = self.addPlot(row=2, col=1, rowspan=1, colspan=1)
        self.yaw = self.addPlot(row=3, col=1, rowspan=1, colspan=1)
    
        self.location.setXRange(-15, 15)
        self.location.setYRange(-15, 15)
        self.location.setAspectLocked()
        self.height.setXRange(0, 200)
        self.v_x.setXRange(0, 200)
        self.v_y.setXRange(0, 200)
        self.v_z.setXRange(0, 200)
        self.yaw.setXRange(0, 200)
        self.yaw.setYRange(-180, 180)
        
        self.location.setLabel('top', text="航迹俯视图(m)")
        self.height.setLabel('top', text="高度(m)")
        self.v_x.setLabel('top', text='Vx(m/s)')
        self.v_y.setLabel('top', text='Vy(m/s)')
        self.v_z.setLabel('top', text='Vz(m/s)')
        self.yaw.setLabel('top', text='yaw(deg)')

        self.location_curve = self.location.plot()
        self.height_curve = self.height.plot()
        self.v_x_curve = self.v_x.plot()
        self.v_y_curve = self.v_y.plot()
        self.v_z_curve = self.v_z.plot()
        self.yaw_curve = self.yaw.plot()

    def update(self, pose_data_queue):
        if pose_data_queue != []:
            data = np.asarray(pose_data_queue, dtype=np.float)
            location_x = data[..., 0]
            location_y = data[..., 1]
            height = data[..., 2]
            v_x = data[..., 3]
            v_y = data[..., 4]
            v_z = data[..., 5]
            yaw = data[..., 6]
            t = linspace(0, len(pose_data_queue) - 1, len(pose_data_queue))
            self.location_curve.setData(location_x, location_y)
            self.height_curve.setData(t, height)
            self.v_x_curve.setData(t, v_x)
            self.v_y_curve.setData(t, v_y)
            self.v_z_curve.setData(t, v_z)
            self.yaw_curve.setData(t, yaw)

class ControlWidget(QWidget):
    def __init__(self, server):
        super().__init__()
        self.server = server
        # Widgets: Buttons, Sliders, ...
        self.start_mission_button = QPushButton("开始新任务", self)
        self.pause_mission_button = QPushButton("暂停任务", self)
        self.continue_mission_button = QPushButton("继续任务", self)

        self.start_video_recording_button = QPushButton("录制视频", self)
        self.stop_video_recording_button = QPushButton("停止", self)

        self.start_data_saving_button = QPushButton("保存数据", self)
        self.stop_data_saving_button = QPushButton("停止", self)

        self.start_streaming_button = QPushButton("开始图传", self)
        self.stop_streaming_button = QPushButton("停止", self)

        self.tune_button = QPushButton("调参", self)
        self.remote_control_button = QPushButton("遥控", self)
        self.advanced_analysis_button = QPushButton("高级分析", self)

        # Signals
        self.start_video_recording_button.clicked.connect(self.start_video_recording)
        self.stop_video_recording_button.clicked.connect(self.stop_video_recording)

        self.start_data_saving_button.clicked.connect(self.start_data_saving)
        self.stop_data_saving_button.clicked.connect(self.stop_data_saving)

        self.start_streaming_button.clicked.connect(self.start_streaming)
        self.stop_streaming_button.clicked.connect(self.stop_streaming)

        # Widgets layout
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.start_mission_button, 0, 0, 1, 2)
        self.layout.addWidget(self.pause_mission_button, 0, 2, 1, 2)
        self.layout.addWidget(self.continue_mission_button, 0, 4, 1, 2)

        self.layout.addWidget(self.start_video_recording_button, 1, 0, 1, 1)
        self.layout.addWidget(self.stop_video_recording_button, 1, 1, 1, 1)
        self.layout.addWidget(self.start_data_saving_button, 2, 0, 1, 1)
        self.layout.addWidget(self.stop_data_saving_button, 2, 1, 1, 1)
        self.layout.addWidget(self.start_streaming_button, 3, 0, 1, 1)
        self.layout.addWidget(self.stop_streaming_button, 3, 1, 1, 1)

        self.layout.addWidget(self.tune_button, 1, 4, 1, 2)
        self.layout.addWidget(self.remote_control_button, 2, 4, 1, 2)
        self.layout.addWidget(self.advanced_analysis_button, 2, 4, 1, 2)
    def start_streaming(self):
        buffer = struct.pack('<?', True)
        self.server.send_msg(buffer, 1, 4)
    def stop_streaming(self):
        buffer = struct.pack('<?', False)
        self.server.send_msg(buffer, 1, 4)
    def start_video_recording(self):
        buffer = struct.pack('<?', True)
        self.server.send_msg(buffer, 1, 5)
    def stop_video_recording(self):
        buffer = struct.pack('<?', False)
        self.server.send_msg(buffer, 1, 5)
    def start_data_saving(self):
        return
    def stop_data_saving(self):
        return

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