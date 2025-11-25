import asyncio
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF

import code_widget
import docx_widget
import settings_widget
from config_setup import cfg, language_names
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = AsyncOpenAI(api_key=cfg.openai_key.value)


qconfig.load("config.json", cfg)
print(cfg)


class Window(FluentWindow):
    """Main Interface"""

    def __init__(self):
        super().__init__()

        setTheme(Theme.AUTO)
        self.setMicaEffectEnabled(True)

        # Create sub-interfaces, when actually using, replace Widget with your own sub-interface
        self.makeDocx = docx_widget.DocxWidget()
        self.saveCodeInterface = code_widget.CodeWidget(client=client)
        self.settingInterface = settings_widget.SettingsWidget()

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.navigationInterface.addSeparator()

        self.addSubInterface(self.makeDocx, FIF.DOCUMENT, "Make DOCX")
        self.addSubInterface(self.saveCodeInterface, FIF.CODE, "Save Code to Dir")

        self.navigationInterface.addSeparator()

        self.addSubInterface(
            self.settingInterface,
            FIF.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM,
        )

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon("app_ico.ico"))
        self.setWindowTitle("SaveCodeX")
