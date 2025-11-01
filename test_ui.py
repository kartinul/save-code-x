from qframelesswindow import AcrylicWindow
from PyQt5.QtWidgets import QApplication, QLabel
import sys


class TestWin(AcrylicWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Acrylic")
        self.resize(400, 300)
        label = QLabel("Hello Acrylic", self)
        label.move(20, 20)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TestWin()
    w.show()
    sys.exit(app.exec_())
