import os
import subprocess
import asyncio

from PyQt5.QtCore import Qt, QThread, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QGuiApplication, QKeySequence
from PyQt5.QtWidgets import (
    QFrame,
    QShortcut,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QMessageBox,
)

from qfluentwidgets import (
    SubtitleLabel,
    Dialog,
    TextEdit,
    ComboBox,
    BodyLabel,
    SettingCardGroup,
    Flyout,
    PushSettingCard,
    ComboBoxSettingCard,
    PrimaryPushButton,
    InfoBar,
    InfoBarPosition,
    IndeterminateProgressRing,
    FlyoutView,
    qconfig,
    setFont,
)
from qfluentwidgets import FluentIcon as FIF

from compile_docx import genFilenameCodeDict, genPropt, sort_key
from config_setup import cfg, language_names

qconfig.load("config.json", cfg)
print(cfg)


class DocxWorker(QThread):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, folder, res):
        super().__init__()
        self.folder = folder
        self.res = res

    def run(self):
        try:
            print(self.res)
            import compile_docx

            lang_conf = next(
                (l for l in cfg.languages.value if l["name"] == cfg.language.value),
                None,
            )
            if not lang_conf:
                raise ValueError("Invalid language config")

            docx_path = compile_docx.generateDocx(
                self.folder + "/",
                res=self.res,
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
        topBar = QHBoxLayout()
        topBar.setSpacing(12)

        title = SubtitleLabel("📄 Convert Code to DOCX Document")
        setFont(title, 28)
        desc = BodyLabel(
            "Select your source directory, choose language, and convert to DOCX."
        )
        desc.setWordWrap(True)

        self.semiAutoAi = ComboBox()
        self.semiAutoAi.addItems(["Full Auto", "Semi Auto"])
        topBar.addWidget(title, 0, Qt.AlignLeft)
        topBar.addWidget(self.semiAutoAi, 0, Qt.AlignRight)

        layout.addLayout(topBar)
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
        if self.semiAutoAi.currentText() == "Full Auto":
            self.genDocx()
        elif self.semiAutoAi.currentText() == "Semi Auto":
            self.genSemiAutoAI()

    def genSemiAutoAI(self):
        lang_conf = next(
            (l for l in cfg.languages.value if l["name"] == cfg.language.value),
            None,
        )
        extension = lang_conf["extension"]
        pathStr = self.selectedFolder
        print(pathStr)
        path = os.fsencode(pathStr)
        listDir = os.listdir(path)
        listDir.sort(key=sort_key)

        filenameCodeDict = genFilenameCodeDict(pathStr, extension, listDir)
        prompt = genPropt(extension, filenameCodeDict)

        QGuiApplication.clipboard().setText(prompt)

        self.openPasteDialog()

        pass

    def genDocx(self, res=None):
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

        self.worker = DocxWorker(self.selectedFolder, res)
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
            title="Done",
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
            title="Generation Failed",
            content=str(err),
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self,
        )

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

    def selectFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.selectedFolder = folder
            self.folderCard.setContent(folder)

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

    def openPasteDialog(self):
        # Fluent dialog, but we’ll hide the title bar anyway
        self.pasteDialog = Dialog(
            title="Prompt Copied",
            content="Paste the prompt into an AI Model, then paste the response json below",  # no built-in content text, we add our own
            parent=self,
        )

        # ❌ remove title bar completely (no weird margins up top)
        self.pasteDialog.setTitleBarVisible(False)

        # ✅ use the internal vertical layout for content
        layout = getattr(self.pasteDialog, "vBoxLayout", self.pasteDialog.layout())
        layout.setContentsMargins(32, 12, 32, 28)
        layout.setSpacing(20)

        # main paste box
        self.pasteIndicator = BodyLabel(
            "Press Ctrl + V to paste response JSON",
            self.pasteDialog,
        )
        self.pasteIndicator.setAlignment(Qt.AlignCenter)
        self.pasteIndicator.setMinimumSize(360, 200)
        self.pasteIndicator.setStyleSheet(
            """
            QLabel {
                border: 2px dashed rgba(160,160,160,0.55);
                border-radius: 20px;
                padding: 32px;
                background-color: rgba(255,255,255,0.06);
                color: rgba(235,235,235,0.96);
            }
            """
        )

        layout.addWidget(self.pasteIndicator)

        # ❌ kill footer/buttons so no dark bar at bottom
        if hasattr(self.pasteDialog, "buttonGroup"):
            self.pasteDialog.buttonGroup.hide()
        else:
            if hasattr(self.pasteDialog, "yesButton"):
                self.pasteDialog.yesButton.hide()
            if hasattr(self.pasteDialog, "cancelButton"):
                self.pasteDialog.cancelButton.hide()

        # Ctrl+V shortcut bound to this dialog
        self.pasteShortcut = QShortcut(QKeySequence("Ctrl+V"), self.pasteDialog)
        self.pasteShortcut.activated.connect(self._handlePasteIntoDialog)

        # don’t close on alt-tab
        self.pasteDialog.setWindowModality(Qt.ApplicationModal)

        self.pasteDialog.resize(480, 320)
        self.pasteDialog.show()
        self.pasteDialog.activateWindow()
        self.pasteDialog.setFocus()

    def _handlePasteIntoDialog(self):
        text = QGuiApplication.clipboard().text().strip()
        if not text:
            return

        self.pasteIndicator.setText("Received")
        self.pasteIndicator.repaint()

        self.pasteDialog.close()
        self.genDocx(text)
