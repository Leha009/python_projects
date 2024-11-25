import sys

from PyQt6.QtWidgets import QApplication

from client import MessengerWidget
from server import ServerWidget

if __name__ == "__main__":
    app = QApplication([])
    if len(sys.argv) == 3:
        window = ServerWidget(sys.argv[1], int(sys.argv[2]))
    else:
        window = MessengerWidget()
    window.show()
    app.exec()
