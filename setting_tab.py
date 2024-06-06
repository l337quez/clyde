from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import Slot

class SettingTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.info_layout = QVBoxLayout()
        
        # Descripción del proyecto
        self.project_description_label = QLabel("Agregar respaldo de db y opción de agregar db, se debe eliminar la que está y agregar la nueva")
        self.info_layout.addWidget(self.project_description_label)

        # Botón para cambiar el tema
        self.theme_button = QPushButton("Cambiar Tema")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.info_layout.addWidget(self.theme_button)

        # Etiqueta para indicar el estado del tema
        self.theme_label = QLabel("Tema Claro")
        self.info_layout.addWidget(self.theme_label)
        
        self.setLayout(self.info_layout)
        self.dark_mode = False  # Estado inicial del tema

    @Slot()
    def toggle_theme(self):
        if self.dark_mode:
            # Cambiar a tema claro
            self.main_window.setStyleSheet("")
            self.theme_label.setText("Tema Claro")
        else:
            # Cambiar a tema oscuro
            dark_style_sheet = """
            QWidget {
                background-color: #2e2e2e;
                color: #ffffff;
            }
            QTabBar::tab {
                background-color: #3e3e3e;
                color: #ffffff;
                padding: 10px;
            }
            QTabBar::tab:selected {
                background-color: #5e5e5e;
            }
            QPushButton {
                background-color: #3e3e3e;
                color: #ffffff;
                border: 1px solid #ffffff;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #4e4e4e;
            }
            QTableWidget {
                background-color: #3e3e3e;
                color: #ffffff;
                gridline-color: #5e5e5e;
                border: 1px solid #5e5e5e;
            }
            QHeaderView::section {
                background-color: #3e3e3e;
                color: #ffffff;
                border: 1px solid #5e5e5e;
            }
            """
            self.main_window.setStyleSheet(dark_style_sheet)
            self.theme_label.setText("Tema Oscuro")

        self.dark_mode = not self.dark_mode