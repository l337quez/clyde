from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog, QTextEdit)
from PySide6.QtCore import Slot, QTimer
from pacmanprogress import Pacman
from backup_restore_threads import BackupThread, LoadThread
import os
import json
import sys

class SettingTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.info_layout = QVBoxLayout()
        
        # Layout horizontal para el botón y la etiqueta
        self.theme_layout = QHBoxLayout()
        
        # Botón para cambiar el tema
        self.theme_button = QPushButton("Change Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_layout.addWidget(self.theme_button)

        # Etiqueta para indicar el estado del tema
        self.theme_label = QLabel("Light Theme")
        self.theme_layout.addWidget(self.theme_label)
        
        # Añadir el layout horizontal al layout principal
        self.info_layout.addLayout(self.theme_layout)

        # Botones para respaldar y cargar la base de datos
        self.backup_button = QPushButton("Respaldo DB")
        self.backup_button.clicked.connect(self.backup_db)
        self.info_layout.addWidget(self.backup_button)

        self.load_button = QPushButton("Cargar DB")
        self.load_button.clicked.connect(self.load_db)
        self.info_layout.addWidget(self.load_button)

        # Botón para iniciar la animación de la barra de progreso
        self.animate_button = QPushButton("Iniciar Animación")
        self.animate_button.clicked.connect(self.start_animation)
        self.info_layout.addWidget(self.animate_button)

        # QLabel para la barra de progreso
        self.progress_label = QLabel("")
        self.info_layout.addWidget(self.progress_label)

        # Área de texto para mostrar mensajes de error o estado
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.info_layout.addWidget(self.status_text)

        self.setLayout(self.info_layout)

        # Cargar el tema desde el archivo de configuración
        config = self.load_config()
        self.dark_mode = config.get("dark_mode", False)

        # Aplicar el estado correcto directamente (sin activar toggle_theme)
        if self.dark_mode:
            qss_file = self.get_qss_path()
            with open(qss_file, "r") as file:
                self.main_window.setStyleSheet(file.read())
            self.theme_label.setText("Dark Theme")
        else:
            self.main_window.setStyleSheet("")
            self.theme_label.setText("Light Theme")



    def get_config_path(self):
        config_dir = os.path.join(os.path.expanduser("~"), ".myapp")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.json")

    # def save_config(self, config_data):
    #     config_path = self.get_config_path()
    #     with open(config_path, "w") as config_file:
    #         json.dump(config_data, config_file)

    def save_config(self, updated_data):
        config_path = self.get_config_path()
        config = {}

        # Cargar config existente si existe
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)

        # Actualizar solo los campos necesarios
        config.update(updated_data)

        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)


    def load_config(self):
        config_path = self.get_config_path()
        if os.path.exists(config_path):
            with open(config_path, "r") as config_file:
                return json.load(config_file)
        return {}

    def get_qss_path(self):
        if getattr(sys, 'frozen', False):
            # Estamos empaquetados con PyInstaller
            base_path = sys._MEIPASS
        else:
            # Estamos en modo de desarrollo
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, "dark_theme.qss")

    # @Slot()
    # def toggle_theme(self):
    #     if self.dark_mode:
    #         # Cambiar a tema claro
    #         self.main_window.setStyleSheet("")
    #         self.theme_label.setText("Light Theme")
    #         config = {"theme": "light"}
    #     else:
    #         # Cambiar a tema oscuro
    #         qss_file = self.get_qss_path()
    #         with open(qss_file, "r") as file:
    #             self.main_window.setStyleSheet(file.read())
    #         self.theme_label.setText("Dark Theme")
    #         config = {"theme": "dark"}

    #     self.save_config(config)
    #     self.dark_mode = not self.dark_mode

    @Slot()
    def toggle_theme(self):
        config_update = {}

        if self.dark_mode:
            # Cambiar a tema claro
            self.main_window.setStyleSheet("")
            self.theme_label.setText("Light Theme")
            config_update = {"dark_mode": False}
        else:
            # Cambiar a tema oscuro
            qss_file = self.get_qss_path()
            with open(qss_file, "r") as file:
                self.main_window.setStyleSheet(file.read())
            self.theme_label.setText("Dark Theme")
            config_update = {"dark_mode": True}

        self.save_config(config_update)
        self.dark_mode = not self.dark_mode


    @Slot()
    def backup_db(self):
        file_dialog = QFileDialog()
        file_path = QFileDialog.getExistingDirectory(self, "Guardar Respaldo de DB")
        
        if file_path:
            self.backup_thread = BackupThread(self.main_window.db_name, file_path)
            self.backup_thread.status_signal.connect(self.status_text.append)
            self.backup_thread.finished_signal.connect(self.on_backup_finished)
            self.status_text.clear()
            self.status_text.append("Iniciando respaldo...\n")

            # Iniciar el hilo de respaldo
            self.backup_thread.start()

            # Iniciar la barra de progreso Pacman
            self.pacman = Pacman(self.progress_label, start=0, end=100, width=35, text="Respaldo DB", candy_count=35)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_pacman)
            self.timer.start(100)

    @Slot()
    def load_db(self):
        file_dialog = QFileDialog()
        file_path = QFileDialog.getExistingDirectory(self, "Cargar Respaldo de DB")

        if file_path:
            self.load_thread = LoadThread(self.main_window.db_name, file_path)
            self.load_thread.status_signal.connect(self.status_text.append)
            self.load_thread.finished_signal.connect(self.on_load_finished)
            self.status_text.clear()
            self.status_text.append("Iniciando carga...\n")

            # Iniciar el hilo de carga
            self.load_thread.start()

            # Iniciar la barra de progreso Pacman
            self.pacman = Pacman(self.progress_label, start=0, end=100, width=35, text="Cargar DB", candy_count=35)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_pacman)
            self.timer.start(100)

    @Slot()
    def start_animation(self):
        self.pacman = Pacman(self.progress_label, start=0, end=100, width=35, text="Progress", candy_count=35)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pacman)
        self.timer.start(100)

    @Slot()
    def update_pacman(self):
        self.pacman.update(1)
        if self.pacman.step >= self.pacman.end:
            self.timer.stop()

    @Slot()
    def on_backup_finished(self):
        self.status_text.append("Respaldo completado.")
        self.timer.stop()

    @Slot()
    def on_load_finished(self):
        self.status_text.append("Carga completada.")
        self.timer.stop()
