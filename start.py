import configparser
import os
import sys
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow

from server import UdpServer

CONFIG_FILE = "ground_control.cfg"
if not os.path.exists(os.path.join(os.getcwd(), CONFIG_FILE)):
    print("[ERROR]: no gound_control.cfg found")
    sys.exit()
CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_FILE)

UDP_HOST = CONFIG.get("UDP", "HOST")
UDP_PORT = CONFIG.getint("UDP", "PORT")

UDP_SERVER = UdpServer(UDP_HOST, UDP_PORT)
APP = QApplication([])
MAIN_WINDOW = MainWindow(UDP_SERVER)
MAIN_WINDOW.show()
APP.exit(APP.exec_())
sys.exit()
