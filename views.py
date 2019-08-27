# -*- coding: utf-8 -*
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QWidget, QPushButton, QLabel
import numpy as np
from numpy import linspace
import pyqtgraph as pg
#from mem_top import mem_top
import struct
import sys
if '/opt/ros/kinetic/lib/python2.7/dist-packages' in sys.path:
    sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2

class StateParamPanel(QWidget):
    def __init__(self):
        super().__init__()
        # Widgets: Buttons, Sliders, ...
        self.video_streaming_label = QLabel()
        # Widgets layout
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.video_streaming_label, 0, 0)
    def update(self, state_param_queue):
        if state_param_queue == []:
            return
        param = state_param_queue[0]
        self.video_streaming_label.setText("录制开启: " + str(param[1]))

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

        self.start_video_streaming_button = QPushButton("开始图传", self)
        self.stop_video_streaming_button = QPushButton("停止", self)

        # Signals
        self.start_video_recording_button.clicked.connect(self.start_video_recording)
        self.stop_video_recording_button.clicked.connect(self.stop_video_recording)

        self.start_data_saving_button.clicked.connect(self.start_data_saving)
        self.stop_data_saving_button.clicked.connect(self.stop_data_saving)

        self.start_video_streaming_button.clicked.connect(self.start_video_streaming)
        self.stop_video_streaming_button.clicked.connect(self.stop_video_streaming)

        # Widgets layout
        self.layout = QGridLayout(self)

        self.layout.addWidget(self.start_mission_button, 0, 0)
        self.layout.addWidget(self.pause_mission_button, 0, 1)
        self.layout.addWidget(self.continue_mission_button, 0, 2)

        self.layout.addWidget(self.start_video_recording_button, 1, 0)
        self.layout.addWidget(self.stop_video_recording_button, 1, 1)
        self.layout.addWidget(self.start_data_saving_button, 2, 0)
        self.layout.addWidget(self.stop_data_saving_button, 2, 1)
        self.layout.addWidget(self.start_video_streaming_button, 3, 0)
        self.layout.addWidget(self.stop_video_streaming_button, 3, 1)
    def start_video_streaming(self):
        buffer = struct.pack('<?', True)
        self.server.send_msg(buffer, 1, 4)
    def stop_video_streaming(self):
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

class Canvas(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        # Widgets layout
        self.visual_x_plot = self.addPlot(row=0, col=0)
        self.visual_y_plot = self.addPlot(row=1, col=0)
        self.visual_z_plot = self.addPlot(row=2, col=0)
        self.visual_pose_plot = self.addPlot(row=3, col=0)
        self.p5 = self.addPlot(row=4, col=0)
        self.p6 = self.addPlot(row=5, col=0)
        self.location = self.addPlot(row=0, col=1, rowspan=3, colspan=1)
        self.height = self.addPlot(row=3, col=1)
        self.vx = self.addPlot(row=4, col=1)
        self.vy = self.addPlot(row=5, col=1)

        self.visual_x_plot.setXRange(0, 200)
        self.visual_y_plot.setXRange(0, 200)
        self.visual_z_plot.setXRange(0, 200)
        self.visual_pose_plot.setXRange(0, 200)
        self.p5.setXRange(0, 200)
        self.p6.setXRange(0, 200)
        self.location.setXRange(-15, 15)
        self.location.setYRange(-15, 15)
        self.location.setAspectLocked()
        self.height.setXRange(0, 200)
        self.vx.setXRange(0, 200)
        self.vy.setXRange(0, 200)

        self.visual_x_plot.setLabel('left', text="相对位置x(cm)")
        self.visual_y_plot.setLabel('left', text="相对位置y(cm)")
        self.visual_z_plot.setLabel('left', text="相对位置z(cm)")
        self.visual_pose_plot.setLabel('left', text="相对位姿R(deg)")
        self.p5.setLabel('left', text="相对位姿P(deg)")
        self.p6.setLabel('left', text="相对位姿Y(deg)")
        self.location.setLabel('top', text="航迹俯视图")
        self.height.setLabel('left', text="uav高度h(m)")
        self.vx.setLabel('left', text="uav水平速度Vx(m/s)")
        self.vy.setLabel('left', text="uav水平速度Vy(m/s)")

        self.visual_x_curve = self.visual_x_plot.plot()
        self.visual_y_curve = self.visual_y_plot.plot()
        self.visual_z_curve = self.visual_z_plot.plot()
        self.visual_pose_r_curve = self.visual_pose_plot.plot()
        self.visual_pose_p_curve = self.visual_pose_plot.plot()
        self.visual_pose_y_curve = self.visual_pose_plot.plot()
        self.location_curve = self.location.plot()
        self.height_curve = self.height.plot()
        self.vx_curve = self.vx.plot()
        self.vy_curve = self.vy.plot()
    def update(self, visual_data_queue, sensor_data_queue):
        if visual_data_queue != []:
            data = np.asarray(visual_data_queue, dtype=np.float)
            visual_x_plot = data[..., 0]
            visual_y = data[..., 1]
            visual_z = data[..., 2]
            visual_R = data[..., 3]
            visual_P = data[..., 4]
            visual_Y = data[..., 5]
            t = linspace(0, len(visual_data_queue) - 1, len(visual_data_queue))
            self.visual_x_curve.setData(t, visual_x_plot, pen=pg.mkPen(color='r'))
            self.visual_y_curve.setData(t, visual_y, pen=pg.mkPen(color='g'))
            self.visual_z_curve.setData(t, visual_z, pen=pg.mkPen(color='b'))
            self.visual_pose_r_curve.setData(t, visual_R, pen=pg.mkPen(color='r'))
            self.visual_pose_p_curve.setData(t, visual_P, pen=pg.mkPen(color='g'))
            self.visual_pose_y_curve.setData(t, visual_Y, pen=pg.mkPen(color='b'))
        if sensor_data_queue != []:
            data = np.asarray(sensor_data_queue, dtype=np.float)
            x = data[..., 0]
            y = data[..., 1]
            z = data[..., 2]
            vx = data[..., 3]
            vy = data[..., 4]
            t = linspace(0, len(sensor_data_queue) - 1, len(sensor_data_queue))
            self.location_curve.setData(x, y)
            self.height_curve.setData(t, z)
            self.vx_curve.setData(t, vx)
            self.vy_curve.setData(t, vy)

class MainWindow(QMainWindow):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.central_widget = QWidget()

        # Widgets: Buttons, Sliders, ...
        self.video_widget = pg.GraphicsLayoutWidget()
        self.video_widget_box = self.video_widget.addViewBox()
        self.video_widget_Item = pg.ImageItem()
        self.video_widget_box.addItem(self.video_widget_Item)
        self.canvas = Canvas()
        self.control_widget = ControlWidget(server)
        self.state_param_panel = StateParamPanel()

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
        self.layout.addWidget(self.state_param_panel, 1, 0)
        self.layout.addWidget(self.control_widget, 1, 1)

        self.setCentralWidget(self.central_widget)
    def update(self):
        #print( mem_top())
        frame_queue = self.server.frame_queue.read()
        if frame_queue != []:
            frame = cv2.cvtColor( frame_queue[0], cv2.COLOR_BGR2RGB)
            frame = cv2.rotate( frame, cv2.ROTATE_180 )
            frame = cv2.resize(frame, None, fx=2, fy=2)
            frame = frame.transpose([1,0,2])
            self.video_widget_Item.setImage(frame)
            #frame = pg.ImageItem(frame)
            #frame = pg.ImageItem(frame_queue[0].T)
            #self.video_widget.addItem(frame)
        
        visual_data_queue = self.server.visual_data_queue.read()
        sensor_data_queue = self.server.sensor_data_queue.read()
        self.canvas.update(visual_data_queue, sensor_data_queue)

        state_param_queue = self.server.state_param_queue.read()
        self.state_param_panel.update(state_param_queue)
    def closeEvent(self, event):
        event.accept()
        #self.server.close()
        self.close()

