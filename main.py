import sys
import asyncio
from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

from main_window import Window
from qfluentwidgets import *

if __name__ == "__main__":
    app = QApplication(sys.argv)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = Window()
    window.show()

    with loop:
        loop.run_forever()
