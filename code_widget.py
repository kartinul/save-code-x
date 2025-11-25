from PyQt5.QtCore import Qt, QEvent, QTimer, QMetaObject, Q_ARG, pyqtSlot, QObject
from PyQt5.QtGui import QColor, QFont, QPainter, QIntValidator
from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QSizePolicy,
)

import pyperclip
import asyncio
from qfluentwidgets import (
    ToolButton,
    CheckBox,
    LineEdit,
    ComboBox,
    BodyLabel,
    InfoBar,
    InfoBarPosition,
    IndeterminateProgressRing,
    setFont,
)
from qfluentwidgets import FluentIcon as FIF

from config_setup import cfg
from getName import get_clipboard_code_name
from utils import save_file, commit_file, shortenPath


class CodeWidget(QFrame):
    def __init__(self, parent=None, client=None):
        super().__init__(parent)
        self.setObjectName("CodeWidget")
        self.selectedFolder = None
        self.client = client

        # --- animation settings ---
        self.ANIMATION_SPEED = 30
        self.FILE_SAVED_DURATION = 500

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(40, 40, 40, 40)
        mainLayout.setSpacing(24)

        # --- top bar ---
        topBar = QHBoxLayout()
        topBar.setSpacing(12)

        # Folder picker button
        self.folderBtn = ToolButton(FIF.FOLDER)
        self.folderBtn.setFixedWidth(40)
        self.folderBtn.setToolTip("Select Folder")
        self.folderBtn.clicked.connect(self.selectFolder)
        topBar.addWidget(self.folderBtn, 0, Qt.AlignLeft)

        # QLabel to show folder path (with middle elide)
        self.folderLabel = QLabel("No folder selected")
        self.folderLabel.setStyleSheet("color: gray;")
        self.folderLabel.setFixedWidth(220)
        self.folderLabel.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.folderLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.folderLabel.setWordWrap(False)
        self.folderLabel.setToolTip("Select a folder first")
        self.folderLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # enable eliding (truncating middle part like ".../folder/sub")
        self.folderLabel.setTextFormat(Qt.PlainText)
        self.folderLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.folderLabel.setProperty("elideMode", Qt.ElideMiddle)

        topBar.addWidget(self.folderLabel, 0, Qt.AlignLeft)
        bottomBar = QHBoxLayout()
        bottomBar.addStretch(1)

        self.useAiCheck = CheckBox("Use AI")
        self.useAiCheck.setChecked(False)
        self.useAiCheck.clicked.connect(self.updateFileLabel)
        bottomBar.addWidget(self.useAiCheck, 0, Qt.AlignRight)

        self.autoCommit = CheckBox("Auto Commit")
        self.autoCommit.setChecked(False)
        bottomBar.addWidget(self.autoCommit, 0, Qt.AlignRight)

        mainLayout.addLayout(bottomBar)

        topBar.addStretch(1)

        # --- numeric counter ---
        self.counterBox = LineEdit()
        self.counterBox.setPlaceholderText("1")
        self.counterBox.setText("1")
        self.counterBox.setFixedWidth(60)
        self.counterBox.setAlignment(Qt.AlignCenter)
        self.counterBox.setValidator(QIntValidator(0, 9999))
        self.counterBox.textChanged.connect(self.updateFileLabel)
        topBar.addWidget(self.counterBox)

        # --- extension picker (from cfg.languages) ---
        extensions = []
        for lang in cfg.languages.value:
            ext = lang.get("extension")
            if ext and ext not in extensions:
                extensions.append(ext)

        self.extPicker = ComboBox()
        self.extPicker.addItems(extensions or [".py"])
        self.extPicker.setFixedWidth(90)
        self.extPicker.currentTextChanged.connect(self.updateFileLabel)
        topBar.addWidget(self.extPicker)

        mainLayout.addLayout(topBar)

        # --- central display box ---
        self.centerFrame = QFrame()
        self.centerFrame.setObjectName("centerFrame")
        self.centerFrame.setMinimumHeight(300)
        self.centerFrame.setStyleSheet(
            """
            QFrame#centerFrame {
                border: 2px dashed rgba(120,120,120,0.4);
                border-radius: 16px;
                background-color: rgba(240,240,240,0.05);
            }
        """
        )

        self.centerLabel = BodyLabel("")
        setFont(self.centerLabel, 18)
        self.centerLabel.setAlignment(Qt.AlignCenter)

        frameLayout = QVBoxLayout(self.centerFrame)
        frameLayout.addStretch()
        frameLayout.addWidget(self.centerLabel, 0, Qt.AlignCenter)

        # loading ring
        self.loadingRing = IndeterminateProgressRing(self.centerFrame)
        self.loadingRing.setFixedSize(40, 40)
        self.loadingRing.setVisible(False)
        frameLayout.addWidget(self.loadingRing, 0, Qt.AlignCenter)
        frameLayout.addStretch()

        mainLayout.addWidget(self.centerFrame)
        mainLayout.addStretch(1)

        # initialize text
        self.updateFileLabel()

        # focus + key events
        self.setFocusPolicy(Qt.StrongFocus)
        self.installRecursiveEventFilter(self)

        # animation vars
        self.bubbleRadius = 0
        self.bubbleOpacity = 0
        self.bubbleTimer = QTimer(self)
        self.bubbleTimer.timeout.connect(self.animateBubble)
        self.showText = False
        self.animating = False

    def updateFileLabel(self):
        num = self.counterBox.text().strip() or "1"
        ext = self.extPicker.currentText() or ".py"
        if self.useAiCheck.isChecked():
            self.centerLabel.setText(
                f"Ctrl + V to save file as {num}_[description]{ext}"
            )
        else:
            self.centerLabel.setText(f"Ctrl + V to save file as {num}{ext}")
        self.updateCounterFromFolder()

    def selectFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.selectedFolder = folder
            self.folderBtn.setToolTip(folder)
            InfoBar.success(
                title="Folder Selected",
                content=folder,
                duration=2000,
                position=InfoBarPosition.BOTTOM,
                parent=self,
            )
            short = shortenPath(folder)
            self.folderLabel.setText(short)

            self.updateCounterFromFolder()

    def installRecursiveEventFilter(self, parent):
        parent.installEventFilter(self)
        for child in parent.findChildren(QObject):
            self.installRecursiveEventFilter(child)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
                if self.animating:
                    return True

                if not self.selectedFolder:
                    InfoBar.warning(
                        title="No Folder Selected",
                        content="Please select a folder first",
                        duration=2500,
                        position=InfoBarPosition.BOTTOM,
                        parent=self,
                    )
                    return True

                if not self.client:
                    return True

                self.animating = True
                self.loadingRing.setVisible(True)
                self.centerLabel.setVisible(False)

                asyncio.create_task(self.fetchNameAndSave())
                return True
        return super().eventFilter(obj, event)

    def incrementCount(self):
        try:
            val = int(self.counterBox.text() or "0")
        except ValueError:
            val = 0
        val += 1
        self.counterBox.setText(str(val))

    def triggerSaveAnimation(self, filename: str = None):
        """
        Start the bubble animation. If filename is provided, the InfoBar
        showing the saved filename will be shown AFTER the animation ends.
        """
        self.animating = True
        self.centerLabel.setVisible(False)
        self.bubbleRadius = 0
        self.bubbleOpacity = 1.0
        self.showText = True
        self.bubbleTimer.start(16)

        # schedule reset of animation after duration
        QTimer.singleShot(self.FILE_SAVED_DURATION, self.resetAnimation)

        # if we have a filename, schedule the InfoBar just after reset
        if filename:
            delay = self.FILE_SAVED_DURATION + 80  # small buffer after reset
            QTimer.singleShot(delay, lambda: self.showFileSavedInfo(filename))

    def resetAnimation(self):
        self.bubbleTimer.stop()
        self.bubbleRadius = 0
        self.bubbleOpacity = 0
        self.showText = False
        self.animating = False
        # make sure label is visible before InfoBar shows
        self.centerLabel.setVisible(True)
        self.centerFrame.update()

    def animateBubble(self):
        self.bubbleRadius += self.ANIMATION_SPEED
        self.bubbleOpacity = max(0, self.bubbleOpacity - 0.03)
        self.centerFrame.update()
        if self.bubbleOpacity <= 0:
            self.bubbleTimer.stop()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.bubbleOpacity <= 0 and not self.showText:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        center = self.centerFrame.geometry().center()

        if self.bubbleOpacity > 0:
            color = QColor(0, 150, 255)
            color.setAlphaF(self.bubbleOpacity)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, self.bubbleRadius, self.bubbleRadius)

        if self.showText:
            painter.setPen(Qt.white)
            font = QFont("Segoe UI", 20)
            painter.setFont(font)
            painter.drawText(self.centerFrame.geometry(), Qt.AlignCenter, "File Saved")

    async def fetchNameAndSave(self):
        try:
            use_ai = self.useAiCheck.isChecked()
            auto_commit = self.autoCommit.isChecked()
            count = int(self.counterBox.text() or 0)

            ext = self.extPicker.currentText().strip()
            if use_ai:
                name = await get_clipboard_code_name(self.client)
                filename = f"{count}_{name}{ext}" if name else f"{count}{ext}"
            else:
                filename = f"{count}{ext}"

            pathToSave = self.selectedFolder + "/" + filename

            # just end here silently, no InfoBars
            QMetaObject.invokeMethod(
                self, "finishFetch", Qt.QueuedConnection, Q_ARG(str, filename)
            )

            code = pyperclip.paste()
            save_file(full_path=pathToSave, content=code)

            if auto_commit:
                commit_text = f"Added a new file {filename}"
                commit_file(folder_path=self.selectedFolder, commit_text=commit_text)

        except Exception as e:
            print("Error fetching name:", e)

    @pyqtSlot(str)
    def finishFetch(self, filename):
        self.loadingRing.setVisible(False)

        # nothing returned, quiet cancel
        if not filename:
            self.animating = False
            self.centerLabel.setVisible(True)
            return

        # start animation and ensure InfoBar shows AFTER animation
        self.triggerSaveAnimation(filename)

    def showFileSavedInfo(self, filename):
        # InfoBar called only after animation completely finished
        InfoBar.success(
            title="File Saved",
            content=f"Saved as {filename}",
            duration=1000,
            position=InfoBarPosition.BOTTOM,
            parent=self,
        )

        # increment after InfoBar shows (small delay so it feels natural)
        self.incrementCount()

    def updateCounterFromFolder(self):
        if not self.selectedFolder:
            return

        ext = self.extPicker.currentText().strip()
        if not ext.startswith("."):
            ext = f".{ext}"

        import os, re

        max_num = 0
        num_pattern = re.compile(r"^(\d+)_?.*")

        for fname in os.listdir(self.selectedFolder):
            # check both start with number and ends with selected extension
            if fname.endswith(ext):
                match = num_pattern.match(fname)
                if match:
                    try:
                        num = int(match.group(1))
                        max_num = max(max_num, num)
                    except ValueError:
                        pass

        # set next count
        self.counterBox.setText(str(max_num + 1))
