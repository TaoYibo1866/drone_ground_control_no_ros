from PyQt5.QtWidgets import QApplication

from models import Server
from views import MainWindow

from sys import argv

if len( argv ) == 1:
    host = '192.168.11.27'
else:
    host = '127.0.0.1' #'192.168.199.179'
server = Server(host, 8080)
app = QApplication([])
main_window = MainWindow(server)
main_window.show()
app.exit(app.exec_())
server.close()

