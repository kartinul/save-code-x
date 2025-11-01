import subprocess
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF


class DocxWorker(QThread):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, folder):
        super().__init__()
        self.folder = folder

    def run(self):
        try:
            import compileDocx  # import here to avoid blocking GUI

            docx_path = compileDocx.generateDocx(self.folder + "/")
            self.finished.emit(docx_path)
        except Exception as e:
            self.failed.emit(str(e))


class DocxWidget(QFrame):
    """Simple, clean DOCX interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.selectedFolder = None

        # --- Layout setup ---
        self.hBox = QHBoxLayout(self)
        self.hBox.setAlignment(Qt.AlignCenter)

        self.vBox = QVBoxLayout()
        self.vBox.setAlignment(Qt.AlignCenter)
        self.vBox.setSpacing(18)

        # --- Title and desc ---
        self.title = SubtitleLabel("Make DOCX File")
        setFont(self.title, 26)
        self.title.setAlignment(Qt.AlignCenter)

        self.desc = BodyLabel("Select a folder and generate your DOCX file.")
        self.desc.setAlignment(Qt.AlignCenter)

        # --- Buttons and label ---
        self.selectBtn = PrimaryPushButton("Select Folder")
        self.generateBtn = PrimaryPushButton("Generate DOCX")

        self.fileLabel = BodyLabel("No folder selected")
        self.fileLabel.setAlignment(Qt.AlignCenter)
        self.fileLabel.setWordWrap(True)

        # --- Add to layout ---
        self.vBox.addWidget(self.title)
        self.vBox.addWidget(self.desc)
        self.vBox.addSpacing(10)
        self.vBox.addWidget(self.selectBtn)
        self.vBox.addWidget(self.fileLabel)
        self.vBox.addSpacing(10)
        self.vBox.addWidget(self.generateBtn)
        self.hBox.addLayout(self.vBox)

        # --- Button actions ---
        self.selectBtn.clicked.connect(self.selectFolder)
        self.generateBtn.clicked.connect(self.generateDocx)

        self.setObjectName("Make-Docx-Interface")

    def selectFolder(self):
        """Open folder picker dialog"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.selectedFolder = folder
            self.fileLabel.setText(f"Selected: {folder}")
        else:
            self.selectedFolder = None
            self.fileLabel.setText("No folder selected")

    def generateDocx(self):
        if not self.selectedFolder:
            QMessageBox.warning(self, "No Folder", "Please select a folder first.")
            return

        # 🔵 modern circular loader
        self.progressRing = IndeterminateProgressRing(self)
        self.progressRing.setFixedSize(80, 80)
        self.progressRing.move(
            (self.width() - self.progressRing.width()) // 2,
            (self.height() - self.progressRing.height()) // 2,
        )
        self.progressRing.start()
        self.progressRing.show()
        self.setDisabled(True)

        InfoBar.info(
            title="Generating DOCX...",
            content="Hold tight while we compile your file 👀",
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self,
        )
        QTimer.singleShot(
            1000,
            lambda: InfoBar.warning(
                title="Please don't touch your keyboard 🧠",
                content="The outputs will be shown and taken screenshot of automatically...",
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self,
            ),
        )

        self.worker = DocxWorker(self.selectedFolder)
        self.worker.finished.connect(lambda path: self.onDocxDone(path))
        self.worker.failed.connect(lambda err: self.onDocxFail(err))
        self.worker.start()

    def onDocxDone(self, docx_path):
        self.progressRing.stop()
        self.progressRing.hide()
        self.setDisabled(False)

        subprocess.run(["explorer", docx_path])
        InfoBar.success(
            title="Done ✅",
            content=f"DOCX saved to:\n{docx_path}",
            position=InfoBarPosition.TOP,
            duration=4000,
            parent=self,
        )

    def onDocxFail(self, err):
        self.progressRing.stop()
        self.progressRing.hide()
        self.setDisabled(False)

        InfoBar.error(
            title="Generation Failed 💀",
            content=str(err),
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self,
        )


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)

        if "Make Docx" in text:
            self.button = PrimaryPushButton("Create DOCX", self)
            self.hBoxLayout.addWidget(self.button, alignment=Qt.AlignCenter)

        # Must set a globally unique object name for the sub-interface
        self.setObjectName(text.replace(" ", "-"))


class Window(FluentWindow):
    """Main Interface"""

    def __init__(self):
        super().__init__()

        setTheme(Theme.AUTO)
        # Create sub-interfaces, when actually using, replace Widget with your own sub-interface
        self.makeDocx = DocxWidget()
        self.videoInterface = Widget("Video Interface", self)
        self.settingInterface = Widget("Setting Interface", self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.navigationInterface.addSeparator()

        self.addSubInterface(self.makeDocx, FIF.HOME, "Make DOCX")
        self.addSubInterface(self.videoInterface, FIF.VIDEO, "Video library")

        self.navigationInterface.addSeparator()

        self.addSubInterface(
            self.settingInterface,
            FIF.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM,
        )

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.setWindowTitle("PyQt-Fluent-Widgets")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()
