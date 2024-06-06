from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QListWidgetItem)
from PySide6.QtCore import Slot
import json
from PySide6.QtGui import QIcon


class AboutTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.info_layout = QVBoxLayout()
        self.project_description_label = QLabel("Development by: Ronal Forero")
        self.info_layout.addWidget(self.project_description_label)
        self.setLayout(self.info_layout)


