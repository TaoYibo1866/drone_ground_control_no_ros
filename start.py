from PyQt5.QtWidgets import QApplication

from models import Server
from views import MainWindow

def main():
    server = Server('127.0.0.1', 8080)
    app = QApplication([])
    main_window = MainWindow(server)
    main_window.show()
    app.exit(app.exec_())
    return

main()
