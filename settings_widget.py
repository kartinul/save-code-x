import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF

from config_setup import cfg, language_names


# right after creating self.langGroup:


qconfig.load("settings_config.json", cfg, autoSave=True)


class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        setTheme(Theme.AUTO)

        self.setObjectName("SettingsWidget")

        # --- outer layout that holds the scroll area ---
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(12)

        # --- scroll area (qfluent) so expanding doesn't resize the window ---
        scroll = ScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        # --- content widget inside the scroll area (transparent so theme shows) ---
        content = QWidget()
        content.setAttribute(Qt.WA_TranslucentBackground, True)
        content.setStyleSheet("background: transparent;")
        contentLayout = QVBoxLayout(content)
        contentLayout.setContentsMargins(40, 20, 40, 20)
        contentLayout.setSpacing(12)

        # --- Header ---
        title = SubtitleLabel("Settings")
        desc = BodyLabel(
            "Manage DOCX generation preferences and per-language behavior."
        )
        contentLayout.addWidget(title)
        contentLayout.addWidget(desc)

        # --- DOCX Section ---
        self.docxGroup = SettingCardGroup("DOCX Settings", content)

        self.defaultLangCard = ComboBoxSettingCard(
            cfg.language,
            icon=FIF.CODE,
            title="Default Language",
            content="Choose which language to use by default.",
            texts=language_names,
            parent=self.docxGroup,
        )

        self.pageBreakCard = SwitchSettingCard(
            icon=FIF.PAGE_LEFT,
            title="Insert Page Breaks",
            content="Automatically add a page break between sections.",
            configItem=cfg.pageBreak,
            parent=self.docxGroup,
        )

        # --- Heading text ---
        self.headingCard = SettingCard(
            icon=FIF.QUICK_NOTE,
            title="Heading (H1)",
            content="Top heading in the generated DOCX file.",
            parent=self.docxGroup,
        )
        self.headingEdit = LineEdit(self)
        self.headingEdit.setFixedWidth(200)
        self.headingEdit.setText(cfg.heading.value)
        self.headingCard.hBoxLayout.addWidget(self.headingEdit)

        # --- Paragraph text ---
        self.paragraphCard = SettingCard(
            icon=FIF.QUICK_NOTE,
            title="Paragraph",
            content="Introductory paragraph under the heading.",
            parent=self.docxGroup,
        )
        self.paragraphEdit = LineEdit(self)
        self.paragraphEdit.setFixedWidth(200)
        self.paragraphEdit.setText(cfg.paragraph.value)
        self.paragraphCard.hBoxLayout.addWidget(self.paragraphEdit)

        # Add everything
        self.docxGroup.addSettingCard(self.defaultLangCard)
        self.docxGroup.addSettingCard(self.pageBreakCard)
        self.docxGroup.addSettingCard(self.headingCard)
        self.docxGroup.addSettingCard(self.paragraphCard)

        # --- Language Settings Section (expandable) ---
        self.langGroup = ExpandGroupSettingCard(
            icon=FIF.COMMAND_PROMPT,
            title="Language Specific Settings",
            content="Customize compile & run behavior for each language.",
            parent=content,
        )

        # language selector card inside the expand group
        self.langDropdownCard = SettingCard(
            icon=FIF.CODE,
            title="Select Language",
            content="Choose which language configuration to edit.",
            parent=content,
        )
        self.langDropdown = ComboBox(self)
        self.langDropdown.addItems([l["name"] for l in cfg.languages.value])
        self.langDropdown.currentTextChanged.connect(self.updateLangSettings)
        self.langDropdownCard.hBoxLayout.addWidget(self.langDropdown)
        self.langGroup.addGroupWidget(self.langDropdownCard)

        # container where dynamic per-language SettingCards go
        self.langSettingsContainer = QWidget(content)
        self.langSettingsLayout = QVBoxLayout(self.langSettingsContainer)
        self.langSettingsLayout.setAlignment(Qt.AlignTop)
        self.langSettingsLayout.setContentsMargins(0, 0, 0, 0)
        self.langSettingsLayout.setSpacing(8)
        self.langGroup.addGroupWidget(self.langSettingsContainer)

        self.langGroup.setAlignment(Qt.AlignTop)
        contentLayout.addWidget(self.langGroup)
        contentLayout.addWidget(self.docxGroup)

        # --- Save button placed AFTER groups to avoid pushing them down ---
        self.saveBtn = PrimaryPushButton("Save Changes")
        self.saveBtn.clicked.connect(self.saveConfig)
        contentLayout.addWidget(self.saveBtn, 0, Qt.AlignRight)

        # put content into scroll area and add to outer layout
        scroll.setWidget(content)
        outer.addWidget(scroll)

        # ensure dropdown reflects saved language and expand group visible
        self.langDropdown.setCurrentText(cfg.language.value)
        try:
            self.langGroup.setExpanded(True)
        except Exception:
            pass

        # initial populate
        self.updateLangSettings(cfg.language.value)

    def getLangConfig(self, langName):
        for lang in cfg.languages.value:
            if lang["name"] == langName:
                return lang
        return None

    def updateLangSettings(self, langName):
        # clear container (only widgets inside langSettingsContainer)
        for i in reversed(range(self.langSettingsLayout.count())):
            w = self.langSettingsLayout.itemAt(i).widget()
            if w:
                w.deleteLater()

        langConf = self.getLangConfig(langName)
        if not langConf:
            return

        # helper to create a SettingCard with a LineEdit inside container
        def add_lineedit_card(icon, title, text):
            edit = LineEdit(self.langSettingsContainer)
            edit.setText("" if text is None else text)
            edit.setFixedWidth(400)

            sc = SettingCard(icon=icon, title=title, parent=self.langSettingsContainer)
            sc.hBoxLayout.addWidget(edit, 0, Qt.AlignLeft)
            sc.hBoxLayout.setSpacing(10)

            self.langSettingsLayout.addWidget(sc)
            return edit

        # compile
        self.compileEdit = add_lineedit_card(
            FIF.CODE, "Compile Command", langConf.get("compile", "")
        )
        self.runEdit = add_lineedit_card(
            FIF.PENCIL_INK, "Extension", langConf.get("extension", "")
        )
        # run
        self.extentionEdit = add_lineedit_card(
            FIF.PLAY, "Run Command", langConf.get("run", "")
        )
        # input tags (fall back to "keywords" for older configs)
        self.inputEdit = add_lineedit_card(
            FIF.INFO, "Input Tags", langConf.get("input", langConf.get("keywords", ""))
        )
        # output tags (or empty)
        self.outputEdit = add_lineedit_card(
            FIF.TAG, "Output Tags", langConf.get("output", "")
        )

    def saveConfig(self):
        langName = self.langDropdown.currentText()
        langConf = self.getLangConfig(langName)
        if not langConf:
            return

        langConf["compile"] = self.compileEdit.text()
        langConf["extension"] = self.extentionEdit.text()
        langConf["run"] = self.runEdit.text()
        langConf["input"] = self.inputEdit.text()
        langConf["output"] = self.outputEdit.text()

        cfg.language.value = langName
        cfg.languages.value = cfg.languages.value  # trigger save
        cfg.save()
