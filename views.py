# -*- coding: utf-8 -*
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QWidget, QPushButton, QLabel
import numpy as np
from numpy import linspace
import pyqtgraph as pg

import struct

class ConfigParamPanel(QWidget):
    def __init__(self):
        super().__init__()
        # Widgets: Buttons, Sliders, ...
        self.rec_label = QLabel()
        # Widgets layout
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.rec_label, 0, 0)
    def update(self, config_param_queue):
        if config_param_queue == []:
            return
        param = config_param_queue[0]
        self.rec_label.setText("REC: " + str(param[0]))

class ControlWidget(QWidget):
    def __init__(self, server):
        super().__init__()
        self.server = server
        # Widgets: Buttons, Sliders, ...
        self.start_mission_button = QPushButton("开始任务", self)
        self.pause_mission_button = QPushButton("暂停任务", self)
        self.continue_mission_button = QPushButton("继续任务", self)

        self.start_video_recording_button = QPushButton("录制视频", self)
        self.stop_video_recording_button = QPushButton("停止", self)

        self.start_data_saving_button = QPushButton("保存数据", self)
        self.stop_data_saving_button = QPushButton("停止", self)

        # Signals
        self.start_video_recording_button.clicked.connect(self.start_video_recording)
        self.stop_video_recording_button.clicked.connect(self.stop_video_recording)

        self.start_data_saving_button.clicked.connect(self.start_data_saving)
        self.stop_data_saving_button.clicked.connect(self.stop_data_saving)

        # Widgets layout
        self.layout = QGridLayout(self)

        self.layout.addWidget(self.start_mission_button, 0, 0)
        self.layout.addWidget(self.pause_mission_button, 0, 1)
        self.layout.addWidget(self.continue_mission_button, 0, 2)

        self.layout.addWidget(self.start_video_recording_button, 1, 0)
        self.layout.addWidget(self.stop_video_recording_button, 1, 1)
        self.layout.addWidget(self.start_data_saving_button, 2, 0)
        self.layout.addWidget(self.stop_data_saving_button, 2, 1)
    def start_video_recording(self):
        buffer = struct.pack('<?', True)
        self.server.send_msg(buffer, 1, 4)
    def stop_video_recording(self):
        buffer = struct.pack('<?', False)
        self.server.send_msg(buffer, 1, 4)
    def start_data_saving(self):
        return
    def stop_data_saving(self):
        return

class Canvas(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        # Widgets layout
        self.p1 = self.addPlot(row=0, col=0)
        self.p2 = self.addPlot(row=1, col=0)
        self.p3 = self.addPlot(row=2, col=0)
        self.p4 = self.addPlot(row=3, col=0)
        self.p5 = self.addPlot(row=4, col=0)
        self.p6 = self.addPlot(row=5, col=0)
        self.p7 = self.addPlot(row=0, col=1, rowspan=3, colspan=1)
        self.p8 = self.addPlot(row=3, col=1)
        self.p9 = self.addPlot(row=4, col=1)
        self.p10 = self.addPlot(row=5, col=1)

        self.p1.setXRange(0, 200)
        self.p2.setXRange(0, 200)
        self.p3.setXRange(0, 200)
        self.p4.setXRange(0, 200)
        self.p5.setXRange(0, 200)
        self.p6.setXRange(0, 200)
        self.p7.setXRange(-15, 15)
        self.p7.setYRange(-15, 15)
        self.p7.setAspectLocked()
        self.p8.setXRange(0, 200)
        self.p9.setXRange(0, 200)
        self.p10.setXRange(0, 200)

        self.p1.setLabel('left', text="相对位置x(cm)")
        self.p2.setLabel('left', text="相对位置y(cm)")
        self.p3.setLabel('left', text="相对位置z(cm)")
        self.p4.setLabel('left', text="相对位姿R(deg)")
        self.p5.setLabel('left', text="相对位姿P(deg)")
        self.p6.setLabel('left', text="相对位姿Y(deg)")
        self.p7.setLabel('top', text="航迹俯视图")
        self.p8.setLabel('left', text="uav高度h(m)")
        self.p9.setLabel('left', text="uav水平速度Vx(m/s)")
        self.p10.setLabel('left', text="uav水平速度Vy(m/s)")

        self.curve1 = self.p1.plot()
        self.curve2 = self.p2.plot()
        self.curve3 = self.p3.plot()
        self.curve4 = self.p4.plot()
        self.curve5 = self.p5.plot()
        self.curve6 = self.p6.plot()
        self.curve7 = self.p7.plot()
        self.curve8 = self.p8.plot()
        self.curve9 = self.p9.plot()
        self.curve10 = self.p10.plot()
    def update(self, visual_data_queue, sensor_data_queue):
        if visual_data_queue != []:
            data = np.asarray(visual_data_queue, dtype=np.float)
            visual_x = data[..., 0]
            visual_y = data[..., 1]
            visual_z = data[..., 2]
            visual_R = data[..., 3]
            visual_P = data[..., 4]
            visual_Y = data[..., 5]
            t = linspace(0, len(visual_data_queue) - 1, len(visual_data_queue))
            self.curve1.setData(t, visual_x)
            self.curve2.setData(t, visual_y)
            self.curve3.setData(t, visual_z)
            self.curve4.setData(t, visual_R)
            self.curve5.setData(t, visual_P)
            self.curve6.setData(t, visual_Y)
        if sensor_data_queue != []:
            data = np.asarray(sensor_data_queue, dtype=np.float)
            x = data[..., 0]
            y = data[..., 1]
            z = data[..., 2]
            vx = data[..., 3]
            vy = data[..., 4]
            t = linspace(0, len(sensor_data_queue) - 1, len(sensor_data_queue))
            self.curve7.setData(x, y)
            self.curve8.setData(t, z)
            self.curve9.setData(t, vx)
            self.curve10.setData(t, vy)

class MainWindow(QMainWindow):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.central_widget = QWidget()

        # Widgets: Buttons, Sliders, ...
        self.video_widget = pg.GraphicsView()
        self.canvas = Canvas()
        self.control_widget = ControlWidget(server)
        self.config_param_panel = ConfigParamPanel()

        # Timer for acquiring images at regular intervals
        self.acquisition_timer = QTimer()
        self.acquisition_timer.start(30)
        self.acquisition_timer.timeout.connect(self.update)
        
        self.layout = QGridLayout(self.central_widget)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)
        self.layout.setColumnStretch(4, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)
        self.layout.addWidget(self.video_widget, 0, 0, 1, 2)
        self.layout.addWidget(self.canvas, 0, 2, 2, 3)
        self.layout.addWidget(self.config_param_panel, 1, 0)
        self.layout.addWidget(self.control_widget, 1, 1)

        self.setCentralWidget(self.central_widget)
    def update(self):
        frame_queue = self.server.frame_queue.read()
        if frame_queue == []:
            return
        frame = pg.ImageItem(frame_queue[0].T)
        self.video_widget.addItem(frame)
        
        visual_data_queue = self.server.visual_data_queue.read()
        sensor_data_queue = self.server.sensor_data_queue.read()
        self.canvas.update(visual_data_queue, sensor_data_queue)

        config_param_queue = self.server.config_param_queue.read()
        self.config_param_panel.update(config_param_queue)
    def closeEvent(self, event):
        event.accept()
        self.server.close()
        self.close()

