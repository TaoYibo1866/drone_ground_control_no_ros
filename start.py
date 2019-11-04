import configparser
import os
import sys
from sys import argv
from PyQt5.QtWidgets import QApplication
from windows import MainWindow

from server import UdpServer

CONFIG_FILE = "ground_control.cfg"
if not os.path.exists(os.path.join(os.getcwd(), CONFIG_FILE)):
    print("[ERROR]: no gound_control.cfg found")
    sys.exit()
CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_FILE)

if len(argv) == 2 and argv[1] == "local":
    UDP_HOST = "127.0.0.1"
    print("local")
else:
    UDP_HOST = CONFIG.get("UDP", "HOST")
UDP_PORT = CONFIG.getint("UDP", "PORT")

UDP_SERVER = UdpServer(UDP_HOST, UDP_PORT)
APP = QApplication([])
MAIN_WINDOW = MainWindow(UDP_SERVER)
MAIN_WINDOW.show()
APP.exit(APP.exec_())
sys.exit()
