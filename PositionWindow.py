# -*- coding: utf-8 -*
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QWidget, QPushButton, QLabel
import numpy as np
from numpy import linspace
import pyqtgraph as pg

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
        return
        #if position_queue != []:
        #    data = np.asarray(position_queue, dtype=np.float)
        #    north = data[..., 0]
        #    north_t = data[..., 1]
        #    east = data[..., 2]
        #    east_t = data[..., 3]
        #    down = data[..., 4]
        #    down_t = data[..., 5]
        #    self.north_curve.setData(north_t, north)
        #    self.east_curve.setData(east_t, east)
        #    self.down_curve.setData(down_t, down)     

class PositionWindow(QMainWindow):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.central_widget = QWidget()
        self.position_widget = PositionWidget()

        self.acquisition_timer = QTimer()
        self.acquisition_timer.start(30)
        self.acquisition_timer.timeout.connect(self.update)

        self.layout = QGridLayout(self.central_widget)
        self.layout.addWidget(self.position_widget, 0, 0)

        self.setCentralWidget(self.central_widget)
    def update(self):
        return
        #position_queue = self.server.position_queue.read()
        #self.position_widget.update(position_queue)
