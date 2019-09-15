from PyQt5.QtWidgets import QApplication

from models import UdpServer, TcpServer
from views import MainWindow

from sys import argv
import sys

if len( argv ) == 1:
    host = '192.168.11.27'
elif argv[1] == "local":
    host = '127.0.0.1'
else:
    print("invalid argv!")
udp_server = UdpServer(host, 8080)
tcp_server = TcpServer(host, 8080)
app = QApplication([])
main_window = MainWindow(udp_server, tcp_server)
main_window.show()
app.exit(app.exec_())
sys.exit()

