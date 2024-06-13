from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog, QTextEdit)
from PySide6.QtCore import Slot, QTimer
from pacmanprogress import Pacman
from backup_restore_threads import BackupThread, LoadThread

class SettingTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.info_layout = QVBoxLayout()
        
        # Descripción del proyecto
        self.project_description_label = QLabel("Agregar respaldo de db y opción de agregar db, se debe eliminar la que está y agregar la nueva")
        self.info_layout.addWidget(self.project_description_label)

        # Layout horizontal para el botón y la etiqueta
        self.theme_layout = QHBoxLayout()
        
        # Botón para cambiar el tema
        self.theme_button = QPushButton("Cambiar Tema")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_layout.addWidget(self.theme_button)

        # Etiqueta para indicar el estado del tema
        self.theme_label = QLabel("Tema Claro")
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
            QTabWidget::pane {
                border: 2px solid #2e2e2e;  /* Cambiar el color de borde del área de la pestaña */
            }
            QLineEdit {
                background-color: #3e3e3e;  /* Fondo del campo de entrada */
                color: #ffffff;  /* Color del texto */
                border: 1px solid #5e5e5e;  /* Borde del campo de entrada */
                border-radius: 3px;  /* Opcional: bordes redondeados */
                padding: 5px;  /* Opcional: espacio interno */
            }
            QLineEdit:focus {
                border: 1px solid #4e4e4e;  /* Borde cuando el campo está enfocado */
            }
            """
            self.main_window.setStyleSheet(dark_style_sheet)
            self.theme_label.setText("Tema Oscuro")

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
