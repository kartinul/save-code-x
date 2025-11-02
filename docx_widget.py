import subprocess
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF

from config_setup import cfg, language_names

qconfig.load("config.json", cfg)
print(cfg)


class DocxWorker(QThread):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, folder):
        super().__init__()
        self.folder = folder

    def run(self):
        try:
            import compileDocx  # import here to avoid blocking GUI

            lang_conf = next(
                (l for l in cfg.languages.value if l["name"] == cfg.language.value),
                None,
            )
            if not lang_conf:
                raise ValueError("Invalid language config")

            inputs = [s.strip() for s in lang_conf["input"].split(",") if s.strip()]
            prints = [s.strip() for s in lang_conf["output"].split(",") if s.strip()]

            docx_path = compileDocx.generateDocx(
                self.folder + "/",
                inputScan=inputs,
                printScan=prints,
                extension=lang_conf["extension"],
                compile_cmd=lang_conf["compile"],
                run_cmd=lang_conf["run"],
                page_break=cfg.pageBreak.value,
                heading=cfg.heading.value,
                paragraph=cfg.paragraph.value,
            )

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
            icon=FIF.FOLDER,
            title="Working Directory",
            content="No folder selected",
            parent=self.docxGroup,
        )
        self.folderCard.clicked.connect(self.selectFolder)

        # Language selection card
        self.langCard = ComboBoxSettingCard(
            configItem=cfg.language,
            icon=FIF.CODE,
            title="Language",
            content="Select the programming language of your source files",
            texts=language_names,
            parent=self.docxGroup,
        )

        # Add cards to the group
        self.docxGroup.addSettingCard(self.folderCard)
        self.docxGroup.addSettingCard(self.langCard)

        self.generateBtn = PrimaryPushButton(FIF.DOCUMENT, "Generate")
        self.generateBtn.setFixedSize(QSize(220, 46))
        self.generateBtn.clicked.connect(self.generateDocx)

        layout.addWidget(self.docxGroup)
        layout.addWidget(self.generateBtn, 0, Qt.AlignCenter)
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
                duration=5000,
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

        folder_path = "\\".join(docx_path.split("/")[:-1])
        print(folder_path)
        subprocess.run(["explorer", folder_path])
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
