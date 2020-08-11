# -*- coding: utf-8 -*
import os
import sys
import struct
from datetime import datetime
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QGridLayout, QWidget, QPushButton, QLabel, QFrame, QPlainTextEdit, QTabWidget
import numpy as np
import pyqtgraph as pg
#from mem_top import mem_top
import cv2
import configparser

CONFIG_FILE = "ground_control.cfg"
if not os.path.exists(os.path.join(os.getcwd(), CONFIG_FILE)):
    print("[ERROR]: no gound_control.cfg found")
    sys.exit()
CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_FILE)

SAFE_QUIT_COMMAND = CONFIG.getint("CONTROL_STATUS", "SAFE_QUIT_COMMAND")
FORCE_QUIT_COMMAND = CONFIG.getint("CONTROL_STATUS", "FORCE_QUIT_COMMAND")
ALTITUDE_STEP_COMMAND = CONFIG.getint("CONTROL_STATUS", "ALTITUDE_STEP_COMMAND")
ALTITUDE_STAY_MODE = CONFIG.getint("CONTROL_STATUS", "ALTITUDE_STAY_MODE")
FLOW_HOLD_COMMAND = CONFIG.getint("CONTROL_STATUS", "FLOW_HOLD_COMMAND")
FLOW_HOLD_MODE = CONFIG.getint("CONTROL_STATUS", "FLOW_HOLD_MODE")
VISION_CONTROL_COMMAND = CONFIG.getint("CONTROL_STATUS", "VISION_CONTROL_COMMAND")
WAIT_COMMAND = CONFIG.getint("CONTROL_STATUS", "WAIT_COMMAND")
VISION_OPEN_LOOP_MODE = CONFIG.getint("CONTROL_STATUS", "VISION_OPEN_LOOP_MODE")
SEARCH_RING = CONFIG.getint("CONTROL_STATUS", "SEARCH_RING")

class PositionWidget(QWidget):
    def __init__(self, server):
        QWidget.__init__(self)
        self.run = True
        self.server = server
        self.layout = QGridLayout(self)

        #define plot
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_widget.ci.layout.setRowStretchFactor(0, 2)
        self.plot_widget.ci.layout.setRowStretchFactor(1, 1)
        self.position = self.plot_widget.addPlot(0, 0)
        self.input = self.plot_widget.addPlot(1, 0)
        self.position_n_curve = self.position.plot()
        self.position_e_curve = self.position.plot()
        self.reference_n_curve = self.position.plot()
        self.reference_e_curve = self.position.plot()

        self.roll_curve = self.input.plot()
        self.pitch_curve = self.input.plot()
        self.thrust_curve = self.input.plot()

        self.position.showGrid(x=1, y=1)
        self.position.showAxis("right")
        self.input.showGrid(x=1, y=1)
        self.input.showAxis("right")

        self.layout.addWidget(self.plot_widget, 0, 0, 1, 3)

        self.stop_button = ToggleButton(["保护制动", "紧急手动"], self)
        self.stop_button.clicked.connect(self.stop)
        self.layout.addWidget(self.stop_button, 1, 0)

        self.hold_button = QPushButton("定点", self)
        self.hold_button.clicked.connect(lambda: self.hold(0.0))
        self.layout.addWidget(self.hold_button, 1, 1)

        self.step_button = QPushButton("阶跃x+", self)
        self.step_button.clicked.connect(lambda: self.hold(0.3))
        self.layout.addWidget(self.step_button, 1, 2)
    def update(self):
        if not self.run:
            return
        position_queue = self.server.position_queue.read()
        if position_queue:
            position = np.asarray(position_queue, np.float32)
            position_t = position[:, 0] / 1000
            position_n = position[:, 1]
            position_e = position[:, 2]
            show = position_t > position_t[-1] - 10
            self.position_n_curve.setData(position_t[show], position_n[show], pen=pg.mkPen('r'), symbol='x', symbolSize=1)
            self.position_e_curve.setData(position_t[show], position_e[show], pen=pg.mkPen('g'), symbol='x', symbolSize=1)
            self.position.setXRange(position_t[-1] - 10, position_t[-1])
        reference_ne = self.server.reference_ne_queue.read()
        if reference_ne:
            reference_ne = np.asarray(reference_ne, np.float32)
            reference_t = reference_ne[:, 0] / 1000
            reference_n = reference_ne[:, 1]
            reference_e = reference_ne[:, 2]
            show = reference_t > reference_t[-1] - 10
            self.reference_n_curve.setData(reference_t[show], reference_n[show], pen=pg.mkPen('r'))
            self.reference_e_curve.setData(reference_t[show], reference_e[show], pen=pg.mkPen('g'))
            self.position.setXRange(reference_t[-1] - 10, reference_t[-1])
        input_attitude_queue = self.server.input_attitude_queue.read()
        if input_attitude_queue:
            input_attitude = np.asarray(input_attitude_queue, np.float32)
            input_attitude_t = input_attitude[:, 0] / 1000
            roll = input_attitude[:, 1]
            pitch = input_attitude[:, 2]
            thrust = input_attitude[:, 4]
            show = input_attitude_t > input_attitude_t[-1] - 10
            self.thrust_curve.setData(input_attitude_t[show], thrust[show], pen=pg.mkPen('b'))
            self.roll_curve.setData(input_attitude_t[show], roll[show], pen=pg.mkPen('r'))
            self.pitch_curve.setData(input_attitude_t[show], pitch[show], pen=pg.mkPen('g'))
            self.input.setXRange(input_attitude_t[-1] - 10, input_attitude_t[-1])
    def stop(self):
        if self.stop_button.state == 0:
            buf = struct.pack('<hH4x40x', -2, 0)
            self.server.send_msg(buf, 48, 15)
            self.stop_button.state = 1
            self.stop_button.setText(self.stop_button.text[1])
        elif self.stop_button.state == 1:
            buf = struct.pack('<hH4x40x', -1, 0)
            self.server.send_msg(buf, 48, 15)
            self.stop_button.state = 0
            self.stop_button.setText(self.stop_button.text[0])
    def hold(self, step):
        buf = struct.pack('<hH4xd32x', 2, 1, step)
        self.server.send_msg(buf, 48, 15)
    def mouseDoubleClickEvent(self, _):
        self.run = not self.run

class TargetWidget(QWidget):
    def __init__(self, server):
        QWidget.__init__(self)
        self.run = True
        self.server = server
        self.layout = QGridLayout(self)
            
        #define plot
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_widget.ci.layout.setRowStretchFactor(0, 4)
        self.plot_widget.ci.layout.setRowStretchFactor(1, 1)
        self.position = self.plot_widget.addPlot(0, 0)
        self.confidence = self.plot_widget.addPlot(1, 0)

        self.position.setYRange(-1, 5)
        self.position.showGrid(x=1, y=1)
        self.position.showAxis("right")
        self.confidence.setYRange(0, 1)
        self.confidence.showGrid(x=1, y=1)
        self.confidence.showAxis("right")
        self.x_curve = pg.ScatterPlotItem()
        self.position.addItem(self.x_curve)
        self.y_curve = pg.ScatterPlotItem()
        self.position.addItem(self.y_curve)
        self.z_curve = pg.ScatterPlotItem()
        self.position.addItem(self.z_curve)
        self.confidence_curve = pg.ScatterPlotItem()
        self.confidence.addItem(self.confidence_curve)
        self.layout.addWidget(self.plot_widget, 0, 0, 1, 5)

        self.stop_button = ToggleButton(["刹车", "保护制动", "紧急手动"], self)
        self.stop_button.clicked.connect(self.stop)
        self.layout.addWidget(self.stop_button, 1, 0)

        self.hold_button = QPushButton("定高", self)
        self.hold_button.clicked.connect(lambda: self.hold(0.0))
        self.layout.addWidget(self.hold_button, 1, 1)

        self.step_button = QPushButton("视觉定点", self)
        self.step_button.clicked.connect(lambda: self.vision_hold(0.0))
        self.layout.addWidget(self.step_button, 1, 2)

        self.yaw_pos_button = QPushButton("Yaw+", self)
        self.yaw_pos_button.clicked.connect(lambda: self.vision_hold(5.0))
        self.layout.addWidget(self.yaw_pos_button, 1, 3)

        self.yaw_neg_button = QPushButton("Yaw-", self)
        self.yaw_neg_button.clicked.connect(lambda: self.vision_hold(-5.0))
        self.layout.addWidget(self.yaw_neg_button, 1, 4)
    def update(self):
        if not self.run:
            return
        target_queue = self.server.target_queue.read()
        if target_queue:
            target = np.asarray(target_queue, np.float32)
            target_t = target[:, 0] / 1000
            target_c = target[:, -1]
            target_x = target[:, 3]
            target_y = target[:, 4]
            target_z = target[:, 5]
            show = np.logical_and(target_c > 0, target_t > target_t[-1] - 5)

            self.x_curve.setData(target_t[show], target_x[show], pen=pg.mkPen('r'), symbol='x')
            self.y_curve.setData(target_t[show], target_y[show], pen=pg.mkPen('g'), symbol='x')
            self.z_curve.setData(target_t[show], target_z[show], pen=pg.mkPen('b'), symbol='x')
            self.confidence_curve.setData(target_t[show], target_c[show], symbol='x')

            self.position.setXRange(target_t[-1] - 5, target_t[-1])
            self.confidence.setXRange(target_t[-1] - 5, target_t[-1])
    def stop(self):
        if self.stop_button.state == 0:
            buf = struct.pack('<hH4x40x', -2, 0)
            self.server.send_msg(buf, 48, 15)
            self.stop_button.state = 1
            self.stop_button.setText(self.stop_button.text[1])
        elif self.stop_button.state == 1:
            buf = struct.pack('<hH4x40x', -2, 0)
            self.server.send_msg(buf, 48, 15)
            self.stop_button.state = 2
            self.stop_button.setText(self.stop_button.text[2])
        elif self.stop_button.state == 2:
            buf = struct.pack('<hH4x40x', -1, 0)
            self.server.send_msg(buf, 48, 15)
            self.stop_button.state = 3
            self.stop_button.setText(self.stop_button.text[0])
    def hold(self, step):
        buf = struct.pack('<hH4xd32x', 0, 1, step)
        self.server.send_msg(buf, 48, 15)
    def vision_hold(self, deg):
        buf = struct.pack('<hH4xd32x', 4, 1, deg)
        self.server.send_msg(buf, 48, 15)
    def mouseDoubleClickEvent(self, _):
        self.run = not self.run

class VelocityLoopWidget(QWidget):
    def __init__(self, server):
        QWidget.__init__(self)
        self.run = True
        self.server = server
        self.layout = QGridLayout(self)
        self.plot_widget = pg.GraphicsLayoutWidget()
        #self.plot_widget.ci.layout.setRowStretchFactor(0, 4)
        #self.plot_widget.ci.layout.setRowStretchFactor(1, 1)
        self.velocity = self.plot_widget.addPlot(0, 0)
        self.velocity.showGrid(x=1, y=1)
        self.velocity.showAxis("right")
        self.velocity_x_curve = self.velocity.plot()
        self.velocity_y_curve = self.velocity.plot()
        self.velocity_d_curve = self.velocity.plot()
        self.layout.addWidget(self.plot_widget, 0, 0, 1, 3)

        self.stop_button = ToggleButton(["保护制动", "紧急手动"], self)
        self.stop_button.clicked.connect(self.stop)
        self.layout.addWidget(self.stop_button, 1, 0)

        self.hold_button = QPushButton("定点", self)
        self.hold_button.clicked.connect(lambda: self.hold(0.0))
        self.layout.addWidget(self.hold_button, 1, 1)

        self.step_button = QPushButton("阶跃x+", self)
        self.step_button.clicked.connect(lambda: self.hold(0.3))
        self.layout.addWidget(self.step_button, 1, 2)
    def update(self):
        if not self.run:
            return
        velocity_queue = self.server.velocity_queue.read()
        if velocity_queue:
            velocity = np.asarray(velocity_queue, np.float32)
            velocity_t = velocity[:, 0] / 1000
            velocity_x = velocity[:, 1]
            velocity_y = velocity[:, 2]
            velocity_z = velocity[:, 3]
            show = velocity_t > velocity_t[-1] - 10
            self.velocity_x_curve.setData(velocity_t[show], velocity_x[show], pen=pg.mkPen('r'), name="N")
            self.velocity_y_curve.setData(velocity_t[show], velocity_y[show], pen=pg.mkPen('g'), name="E")
            self.velocity_d_curve.setData(velocity_t[show], velocity_z[show], pen=pg.mkPen('b'), name="D")

            self.velocity.setXRange(velocity_t[-1] - 10, velocity_t[-1])
    def stop(self):
        if self.stop_button.state == 0:
            buf = struct.pack('<hH4x40x', -2, 0)
            self.server.send_msg(buf, 48, 15)
            self.stop_button.state = 1
            self.stop_button.setText(self.stop_button.text[1])
        elif self.stop_button.state == 1:
            buf = struct.pack('<hH4x40x', -1, 0)
            self.server.send_msg(buf, 48, 15)
            self.stop_button.state = 0
            self.stop_button.setText(self.stop_button.text[0])
    def hold(self, step):
        buf = struct.pack('<hH4xd32x', 2, 1, step)
        self.server.send_msg(buf, 48, 15)
    def mouseDoubleClickEvent(self, _):
        self.run = not self.run

class AltitudeLoopWidget(QWidget):
    def __init__(self, server):
        QWidget.__init__(self)
        self.run = True
        self.server = server
        self.layout = QGridLayout(self)
        self.layout.setRowStretch(0, 10)
        self.layout.setRowStretch(1, 1)
        
        #define plot
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_widget.ci.layout.setRowStretchFactor(0, 4)
        self.plot_widget.ci.layout.setRowStretchFactor(1, 1)
        self.altitude = self.plot_widget.addPlot(0, 0)
        self.thrust = self.plot_widget.addPlot(1, 0)
        self.altitude.setYRange(-1, 5)
        self.altitude.showGrid(x=1, y=1)
        self.altitude.showAxis("right")
        self.thrust.setYRange(0, 1)
        self.thrust.showGrid(x=1, y=1)
        self.thrust.showAxis("right")
        self.altitude_curve = self.altitude.plot()
        self.thrust_curve = self.thrust.plot()
        self.reference_curve = self.altitude.plot()
        self.layout.addWidget(self.plot_widget, 0, 0, 1, 5)

        #define button
        self.stop_button = ToggleButton(["保护制动", "紧急手动"], self)
        self.stop_button.clicked.connect(self.stop)
        self.layout.addWidget(self.stop_button, 1, 0)

        self.hold_button = QPushButton("定高", self)
        self.hold_button.clicked.connect(lambda: self.step(0.0))
        self.layout.addWidget(self.hold_button, 1, 1)

        self.step_pos_button = QPushButton("阶跃+", self)
        self.step_pos_button.clicked.connect(lambda: self.step(0.3))
        self.layout.addWidget(self.step_pos_button, 1, 2)

        self.step_neg_button = QPushButton("阶跃-", self)
        self.step_neg_button.clicked.connect(lambda: self.step(-0.3))
        self.layout.addWidget(self.step_neg_button, 1, 3)

        self.save_button = QPushButton("保存", self)
        self.save_button.clicked.connect(self.save)
        self.layout.addWidget(self.save_button, 1, 4)
    def stop(self):
        if self.stop_button.state == 0:
            buf = struct.pack('<hH4x40x', -2, 0)
            self.server.send_msg(buf, 48, 15)
            self.stop_button.state = 1
            self.stop_button.setText(self.stop_button.text[1])
        elif self.stop_button.state == 1:
            buf = struct.pack('<hH4x40x', -1, 0)
            self.server.send_msg(buf, 48, 15)
            self.stop_button.state = 0
            self.stop_button.setText(self.stop_button.text[0])
    def step(self, step):
        buf = struct.pack('<hH4xd32x', 0, 1, step)
        self.server.send_msg(buf, 48, 15)
    def save(self):
        shot = self.grab()
        shot.save(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "altitude.png")
    def update(self):
        if not self.run:
            return
        input_attitude_queue = self.server.input_attitude_queue.read()
        if input_attitude_queue:
            input_attitude = np.asarray(input_attitude_queue, np.float32)
            input_attitude_t = input_attitude[:, 0] / 1000
            thrust = input_attitude[:, 4]
            show = input_attitude_t > input_attitude_t[-1] - 10
            self.thrust_curve.setData(input_attitude_t[show], thrust[show], pen=pg.mkPen('b'))
            self.thrust.setXRange(input_attitude_t[-1] - 10, input_attitude_t[-1])
        reference_queue = self.server.reference_down_queue.read()
        if reference_queue:
            reference = np.asarray(reference_queue, np.float32)
            reference_t = reference[:, 0] / 1000
            reference_alt = -1 * reference[:, 1]
            show = reference_t > reference_t[-1] - 10
            self.reference_curve.setData(reference_t[show], reference_alt[show], pen=pg.mkPen('g'))
            self.altitude.setXRange(reference_t[-1] - 10, reference_t[-1])
        position_queue = self.server.position_queue.read()
        if position_queue:
            position = np.asarray(position_queue, np.float32)
            position_t = position[:, 0] / 1000
            altitude = -1 * position[:, 3]
            show = position_t > position_t[-1] - 10
            self.altitude_curve.setData(position_t[show], altitude[show], pen=pg.mkPen('r'))
            self.altitude.setXRange(position_t[-1] - 10, position_t[-1])
    def mouseDoubleClickEvent(self, _):
        self.run = not self.run

class MissionWidget(QFrame):
    def __init__(self, server):
        QFrame.__init__(self)
        self.server = server
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(1)
        self.layout = QGridLayout(self)
        self.last_status = WAIT_COMMAND

        #define button widget
        self.start_mssion_button = ToggleButton(["开始任务", "保护制动", "紧急手动"], self)
        self.config_button = QPushButton("修改配置文件", self)

        self.start_mssion_button.clicked.connect(self.start_mission)

        self.layout.addWidget(self.start_mssion_button, 0, 0, 1, 1)
        self.layout.addWidget(self.config_button, 1, 0, 1, 1)

        self.video_recording_button = ToggleButton(["录制视频", "结束视频"], self)
        self.video_recording_button.clicked.connect(self.video_recording)
        self.layout.addWidget(self.video_recording_button, 0, 1, 1, 1)

        self.mission_timer = QTimer()
        self.mission_timer.start(30)
        self.mission_timer.timeout.connect(self.update)
    def config(self):
        return
    def start_mission(self):
        if self.start_mssion_button.state == 0:
            buf = struct.pack('<hH4x40x', 99, 0)
            self.server.send_msg(buf, 48, 15)
            self.start_mssion_button.state = 1
            self.start_mssion_button.setText(self.start_mssion_button.text[1])
        elif self.start_mssion_button.state == 1:
            buf = struct.pack('<hH4x40x', -2, 0) #safe land sequence
            self.server.send_msg(buf, 48, 15)
            self.start_mssion_button.state = 2
            self.start_mssion_button.setText(self.start_mssion_button.text[2])
        elif self.start_mssion_button.state == 2:
            buf = struct.pack('<hH4x40x', -1, 0) #emergency quit
            self.server.send_msg(buf, 48, 15)
            self.start_mssion_button.state = 0
            self.start_mssion_button.setText(self.start_mssion_button.text[0])
    def video_recording(self):
        if self.video_recording_button.state == 0:
            buf = struct.pack('<?', True)
            self.server.send_msg(buf, 1, 5)
            self.video_recording_button.state = 1
            self.video_recording_button.setText(self.video_recording_button.text[1])
        elif self.video_recording_button.state == 1:
            buf = struct.pack('<?', False)
            self.server.send_msg(buf, 1, 5)
            self.video_recording_button.state = 0
            self.video_recording_button.setText(self.video_recording_button.text[0])
    def update(self):
        control_status = self.server.control_status_queue.read()
        if control_status:
            status = control_status[-1][1]
            if status == self.last_status:
                return
            self.last_status = status
            # if status == SAFE_QUIT_COMMAND:
            #     QSound(r'vocal/异常保护.wav').play()
            # elif status == FORCE_QUIT_COMMAND:
            #     print("aaaa")
            #     QSound(r'vocal/紧急退出.wav').play()
            # elif status == ALTITUDE_STAY_MODE:
            #     QSound(r'vocal/定高模式.wav').play()
            # elif status == VISION_CONTROL_COMMAND:
            #     QSound(r'vocal/视觉模式.wav').play()
            # elif status == FLOW_HOLD_MODE:
            #     QSound(r'vocal/定点模式.wav').play()

            
class TabWidget(QFrame):
    def __init__(self, server):
        QFrame.__init__(self)
        self.server = server
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(1)
        self.layout = QGridLayout(self)

        self.tab_widget = QTabWidget()
        self.locus_widget = LocusWidget(server)
        self.altitude_loop_widget = AltitudeLoopWidget(server)
        self.velocity_loop_widget = VelocityLoopWidget(server)
        self.target_widget = TargetWidget(server)
        self.position_widget = PositionWidget(server)
        self.tab_widget.addTab(self.altitude_loop_widget, "高度环")
        self.tab_widget.addTab(self.position_widget, "位置环")
        self.tab_widget.addTab(self.velocity_loop_widget, "速度环")
        self.tab_widget.addTab(self.target_widget, "视觉")
        self.tab_widget.addTab(self.locus_widget, "轨迹")

        self.layout.addWidget(self.tab_widget)

        self.tab_timer = QTimer()
        self.tab_timer.start(300)
        self.tab_timer.timeout.connect(self.update)
    def update(self):
        self.tab_widget.currentWidget().update()
        return

class LocusWidget(QWidget):
    def __init__(self, server):
        QWidget.__init__(self)
        self.server = server
        self.layout = QGridLayout(self)
        self.layout.setRowStretch(0, 10)
        self.layout.setRowStretch(1, 1)
        #plot widget
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.map = self.plot_widget.addPlot(row=0, col=0)
        self.map.setXRange(-15, 15)
        self.map.setYRange(-15, 15)
        self.map.setAspectLocked()
        self.map.showGrid(x=1, y=1)
        self.map.showAxis("right")
        self.map.showAxis("top")
        self.map.setTitle("航迹俯视图(m)")
        self.map_curve = self.map.plot()

        self.altitude = self.plot_widget.addPlot(row=0, col=1)
        self.altitude.setYRange(-1, 10)
        self.altitude.showGrid(x=0, y=1)
        self.altitude.showAxis("right", show=True)
        self.altitude.showAxis("bottom", show=False)
        self.altitude.setTitle("高度(m)")
        self.altitude_curve = self.map.plot()

        self.plot_widget.ci.layout.setColumnStretchFactor(0, 8)
        self.plot_widget.ci.layout.setColumnStretchFactor(1, 1)

        self.layout.addWidget(self.plot_widget, 0, 0, 1, 2)
        #button widget
        self.clear_plot_button = QPushButton("清空轨迹")

        self.layout.addWidget(self.clear_plot_button, 1, 0, 1, 1)
    def update(self):
        position_queue = self.server.position_queue.read()
        if position_queue:
            position = np.asarray(position_queue, np.float32)
            position_x = position[:, 1]
            position_y = position[:, 2]
            #position_d = position[:, 3]
            self.map.plot(position_x, position_y)


class CameraWidget(QFrame):
    def __init__(self, server):
        QFrame.__init__(self)
        self.server = server
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(1)
        self.layout = QGridLayout(self)

        #define video widget
        self.camera_widget = pg.GraphicsLayoutWidget()
        self.camera_widget_box = self.camera_widget.addViewBox(0, 0)
        self.camera_widget_box.setAspectLocked()
        self.camera_widget_item = pg.ImageItem()
        self.camera_widget_box.addItem(self.camera_widget_item)

        self.layout.addWidget(self.camera_widget, 0, 0, 1, 3)

        self.camera_timer = QTimer()
        self.camera_timer.start(10)
        self.camera_timer.timeout.connect(self.update)
    def update(self):
        frame_queue = self.server.frame_queue.read()
        if frame_queue:
            frame = cv2.cvtColor(frame_queue[0], cv2.COLOR_BGR2RGB)
            frame = frame.transpose([1, 0, 2])
            frame = cv2.flip(frame, 1)
            self.camera_widget_item.setImage(frame)
            frame_queue.clear()

class LogWidget(QFrame):
    def __init__(self, server):
        QFrame.__init__(self)
        self.server = server
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(1)
        self.layout = QGridLayout(self)
        self.layout.setColumnStretch(0, 30)
        self.layout.setColumnStretch(1, 1)

        self.log_widget = QPlainTextEdit()
        self.log_widget.setReadOnly(True)
        self.layout.addWidget(self.log_widget, 0, 0)

        self.clear_button = QPushButton("清空", self)
        self.clear_button.clicked.connect(self.clear)

        self.layout.addWidget(self.clear_button, 0, 1)

        self.log_timer = QTimer()
        self.log_timer.start(10)
        self.log_timer.timeout.connect(self.update)
    def update(self):
        log_queue = self.server.log_queue.read()
        if log_queue:
            for log in log_queue:
                self.log_widget.appendPlainText(log.decode("utf-8"))
            log_queue.clear()
    def clear(self):
        self.log_widget.setPlainText("")

class TelemWidget(QWidget):
    def __init__(self, server):
        QWidget.__init__(self)
        self.server = server
        self.layout = QGridLayout(self)

        #label widget
        self.flight_mode_label = QLabel("Mode:")
        self.battery_label = QLabel("Battery:")
        self.rc_status_label = QLabel("RC:")
        self.arm_status_label = QLabel("Armed:")
        self.in_air_label = QLabel("inAir:")

        self.height_label = QLabel("高度:m")
        self.roll_label = QLabel("滚转:deg")
        self.pitch_label = QLabel("俯仰:deg")
        self.yaw_label = QLabel("偏航:deg")
        self.velocity_label = QLabel("速度:m/s")
        self.velocity_north_label = QLabel("速度X:m/s")
        self.velocity_east_label = QLabel("速度Y:m/s")
        self.velocity_down_label = QLabel("速度D:m/s")

        self.mission_label = QLabel("任务状态:")
        self.target_label = QLabel("目标:")
        self.target_distance_label = QLabel("距离:")
        self.target_position_x_label = QLabel("位置x:")
        self.target_position_y_label = QLabel("位置y:")
        self.target_position_z_label = QLabel("位置z:")
        
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

        self.mission_label.setFrameShape(QFrame.Box)
        self.target_label.setFrameShape(QFrame.Box)
        self.target_distance_label.setFrameShape(QFrame.Box)
        self.target_position_x_label.setFrameShape(QFrame.Box)
        self.target_position_y_label.setFrameShape(QFrame.Box)
        self.target_position_z_label.setFrameShape(QFrame.Box)

        self.layout.addWidget(self.flight_mode_label, 0, 0, 1, 1)
        self.layout.addWidget(self.battery_label, 1, 0, 1, 1)
        self.layout.addWidget(self.rc_status_label, 2, 0, 1, 1)
        self.layout.addWidget(self.arm_status_label, 3, 0, 1, 1)
        self.layout.addWidget(self.in_air_label, 4, 0, 1, 1)

        self.layout.addWidget(self.height_label, 0, 2, 1, 1)
        self.layout.addWidget(self.roll_label, 1, 2, 1, 1)
        self.layout.addWidget(self.pitch_label, 2, 2, 1, 1)
        self.layout.addWidget(self.yaw_label, 3, 2, 1, 1)
        self.layout.addWidget(self.velocity_label, 0, 3, 1, 1)
        self.layout.addWidget(self.velocity_north_label, 1, 3, 1, 1)
        self.layout.addWidget(self.velocity_east_label, 2, 3, 1, 1)
        self.layout.addWidget(self.velocity_down_label, 3, 3, 1, 1)

        self.layout.addWidget(self.mission_label, 0, 4, 1, 1)
        self.layout.addWidget(self.target_label, 0, 1, 1, 1)
        self.layout.addWidget(self.target_distance_label, 1, 1, 1, 1)
        self.layout.addWidget(self.target_position_x_label, 2, 1, 1, 1)
        self.layout.addWidget(self.target_position_y_label, 3, 1, 1, 1)
        self.layout.addWidget(self.target_position_z_label, 4, 1, 1, 1)

        self.telem_timer = QTimer()
        self.telem_timer.start(300)
        self.telem_timer.timeout.connect(self.update)
    def update(self):
        position_queue = self.server.position_queue.read()
        if position_queue:
            position = position_queue[-1]
            self.height_label.setText("高度: {: 3.1f}m".format(-1 * position[3]))

        velocity_queue = self.server.velocity_queue.read()
        if velocity_queue:
            velocity = velocity_queue[-1]
            self.velocity_label.setText("速度: {: 3.1f}m/s".format(np.linalg.norm(velocity[1:4])))
            self.velocity_north_label.setText("速度X: {: 3.1f}m/s".format(velocity[1]))
            self.velocity_east_label.setText("速度Y: {: 3.1f}m/s".format(velocity[2]))
            self.velocity_down_label.setText("速度D: {: 3.1f}m/s".format(velocity[3]))

        attitude_queue = self.server.attitude_queue.read()
        if attitude_queue:
            attitude = attitude_queue[-1]
            self.roll_label.setText("滚转: {: 3.1f}deg".format(attitude[1]))
            self.pitch_label.setText("俯仰: {: 3.1f}deg".format(attitude[2]))
            self.yaw_label.setText("偏航: {: 3.1f}deg".format(attitude[3]))

        vehicle_status_queue = self.server.vehicle_status_queue.read()
        if vehicle_status_queue:
            status = vehicle_status_queue[-1]
            self.flight_mode_label.setText("Mode: {}".format(status[-1].decode('utf-8')))
            self.battery_label.setText("Battery: {: 2.1f}V {: 2.0f}%".format(status[6], status[7] * 100))
            self.rc_status_label.setText("RC: {} {: 3.0f}".format(status[4], status[5]))
            self.arm_status_label.setText("Armed: {}".format(status[1]))
            self.in_air_label.setText("inAir: {}".format(status[2]))
        
        target_queue = self.server.target_queue.read()
        if target_queue:
            target = target_queue[-1]
            if target[-1] > 0:
                self.target_label.setText("目标: {}".format(target[1]))
                self.target_distance_label.setText("距离: {: 2.1f}m".format(target[2]))
                self.target_position_x_label.setText("位置x: {: 2.1f}m".format(target[3]))
                self.target_position_y_label.setText("位置y: {: 2.1f}m".format(target[4]))
                self.target_position_z_label.setText("位置z: {: 2.1f}m".format(target[5]))
            else:
                self.target_label.setText("目标: {}丢失".format(target[1]))
                self.target_distance_label.setText("距离: {: 2.1f}m".format(target[2]))
                self.target_position_x_label.setText("位置x: {: 2.1f}m".format(target[3]))
                self.target_position_y_label.setText("位置y: {: 2.1f}m".format(target[4]))
                self.target_position_z_label.setText("位置z: {: 2.1f}m".format(target[5]))
        return

class AutoRepeatButton(QPushButton):
    def __init__(self, text, _self):
        QPushButton.__init__(self, text, _self)
        self.setAutoRepeat(True)
        self.setAutoRepeatDelay(0)
        self.setAutoRepeatInterval(10)

class ToggleButton(QPushButton):
    def __init__(self, text, _self):
        QPushButton.__init__(self, text[0], _self)
        self.text = text
        self.state = 0
