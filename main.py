import subprocess
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qfluentwidgets import *
from qframelesswindow import *
from qfluentwidgets import FluentIcon as FIF


class Config(QConfig):
    language = OptionsConfigItem(
        "DOCX", "Language", "Python", OptionsValidator(["C", "C++", "Python"])
    )


cfg = Config()
qconfig.load("config.json", cfg)


class DocxWorker(QThread):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, folder, language):
        super().__init__()
        self.folder = folder
        self.language = language

    def run(self):
        try:
            import compileDocx  # import here to avoid blocking GUI

            docx_path = compileDocx.generateDocx(self.folder + "/", self.language)
            self.finished.emit(docx_path)
        except Exception as e:
            self.failed.emit(str(e))


class DocxWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selectedFolder = None
        self.setObjectName("MakeDocxWidget")

        # --- main layout ---
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(24)

        # --- title & description ---
        title = SubtitleLabel("📄 Convert Code to DOCX Document")
        setFont(title, 28)
        desc = BodyLabel(
            "Select your source directory, choose language, and convert to DOCX."
        )
        desc.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(desc)

        # --- DOCX settings group ---
        self.docxGroup = SettingCardGroup("DOCX Settings", self)

        # Folder selection card
        self.folderCard = PushSettingCard(
            text="Browse",
            icon=FluentIcon.FOLDER,
            title="Working Directory",
            content="No folder selected",
            parent=self.docxGroup,
        )
        self.folderCard.clicked.connect(self.selectFolder)

        # Language selection card
        self.langCard = ComboBoxSettingCard(
            configItem=cfg.language,
            icon=FluentIcon.CODE,
            title="Language",
            content="Select the programming language of your source files",
            texts=["Python", "C"],
            parent=self.docxGroup,
        )

        # Generate DOCX button card
        self.generateCard = PrimaryPushSettingCard(
            text="Generate",
            icon=FluentIcon.DOCUMENT,
            title="Generate DOCX",
            content="Convert your selected code files into a DOCX document",
            parent=self.docxGroup,
        )
        self.generateCard.clicked.connect(self.generateDocx)

        # Add cards to the group
        self.docxGroup.addSettingCard(self.folderCard)
        self.docxGroup.addSettingCard(self.langCard)
        self.docxGroup.addSettingCard(self.generateCard)

        layout.addWidget(self.docxGroup)
        layout.addStretch()

    def selectFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.selectedFolder = folder
            self.folderCard.setContent(folder)

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

        self.worker = DocxWorker(self.selectedFolder, cfg.lanuage.value)
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
        self.setMicaEffectEnabled(True)

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
