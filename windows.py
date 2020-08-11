# -*- coding: utf-8 -*
import struct
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QWidget, QTabWidget
import numpy as np
import pyqtgraph as pg
#from mem_top import mem_top
from widgets import CameraWidget, TelemWidget, TabWidget, MissionWidget, LogWidget

class MainWindow(QMainWindow):
    def __init__(self, server):
        QMainWindow.__init__(self)
        self.server = server
        self.central_widget = QWidget()
        self.layout = QGridLayout(self.central_widget)

        # Widgets: Buttons, Sliders, ...
        self.camera_widget = CameraWidget(server)
        self.tab_widget = TabWidget(server)
        self.telem_widget = TelemWidget(server)
        self.mission_widget = MissionWidget(server)
        self.log_widget = LogWidget(server)

        self.layout.setColumnStretch(0, 3)
        self.layout.setColumnStretch(1, 4)
        self.layout.setRowStretch(0, 5)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 1)
        self.layout.addWidget(self.camera_widget, 0, 0)
        self.layout.addWidget(self.tab_widget, 0, 1)
        self.layout.addWidget(self.mission_widget, 1, 0)
        self.layout.addWidget(self.telem_widget, 1, 1)
        self.layout.addWidget(self.log_widget, 2, 0, 1, 2)

        self.setCentralWidget(self.central_widget)
    def closeEvent(self, event):
        event.accept()
        self.server.close()
        self.close()
