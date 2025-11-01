import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from qfluentwidgets import PrimaryPushButton, setTheme, Theme


def on_click():
    print("Fluent button clicked!")


app = QApplication(sys.argv)

# 🪟 Window setup
window = QWidget()
window.setWindowTitle("My First QFluent App")
window.resize(400, 300)

# 🎨 Apply Fluent theme
setTheme(Theme.AUTO)

# 📦 Layout setup
layout = QVBoxLayout(window)

# 🔘 Add Fluent-style button
btn = PrimaryPushButton("Click Me")
btn.clicked.connect(on_click)

layout.addWidget(btn)
window.setLayout(layout)

# 👀 Show window
window.show()

sys.exit(app.exec())
