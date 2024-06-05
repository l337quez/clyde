from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QListWidgetItem)
from PySide6.QtCore import Slot
import json
from PySide6.QtGui import QIcon


class ProjectAboutTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()


