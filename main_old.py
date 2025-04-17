import sys
import os
from mongolite import Connection
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                               QWidget, QVBoxLayout, QSystemTrayIcon, 
                               QMenu, QListWidget, QScrollArea, QLabel, 
                               QDockWidget, QListWidgetItem, QPushButton)
from PySide6.QtGui import QIcon, QAction, QPixmap, QMovie
from PySide6.QtCore import Slot, Qt, QEvent, QTimer
from project_tab import ProjectTab  # Importar ProjectTab
from project_info_tab import ProjectInfoTab
from project_todo_tab import ProjectTodoTab
from about_tab import AboutTab
from setting_tab import SettingTab
from icon import icon  # Importar los datos del icono desde icon.py

# Establecer explícitamente el ID de modelo de usuario de aplicación en Windows
if sys.platform.startswith('win'):
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'CompanyName.ProductName.SubProduct.VersionInformation')

class GIFLabel(QLabel):
    def __init__(self, gif_path):
        super().__init__()
        self.movie = QMovie(gif_path)
        self.setMovie(self.movie)
        self.movie.start()

    def currentPixmap(self):
        return self.movie.currentPixmap()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GNU Mau")
        self.setGeometry(300, 300, 800, 600)

        # Cargar el icono desde los datos hexadecimales
        qp = QPixmap()
        qp.loadFromData(icon)
        appIcon = QIcon(qp)
        self.setWindowIcon(appIcon)

        # Crear el sistema de bandeja con el ícono
        self.tray_icon = QSystemTrayIcon(appIcon, parent=self)
        self.tray_icon.setToolTip("GNU Mau")
        tray_menu = QMenu()
        show_action = QAction("Mostrar", self)
        quit_action = QAction("Salir", self)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.quit)

        self.tray_icon.show()

        # Inicializar atributos para proyecto actual
        self.current_project_name = ""
        self.current_project_description = ""
        self.current_project_item = None
        self.current_project_info = {}
        self.current_project_id = "default_project_id"
        self.db_name = "projects_db"  # Añadir esta línea para definir db_name

        # Crear la conexión a MongoLite
        print("Conectando a MongoLite...")
        self.client = Connection()
        self.db = self.client[self.db_name]
        self.create_collections()

        # Crear las pestañas
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.project_tab = ProjectTab(self)  # Instanciar ProjectTab
        self.project_info_tab = ProjectInfoTab(self)
        self.project_todo_tab = ProjectTodoTab(self, project_id=self.current_project_id or "default_project_id")
        self.setting_tab = SettingTab(self)  # Pasar self (MainWindow) al constructor
        self.about_tab = AboutTab(self)
        self.tabs.addTab(self.project_tab, "Project")
        self.tabs.addTab(self.project_info_tab, "Information")
        self.tabs.addTab(self.project_todo_tab, "Todo")
        self.tabs.addTab(self.setting_tab, "Setting")
        self.tabs.addTab(self.about_tab, "About")

        # Crear el sidebar con scroll
        self.project_list_widget = QListWidget()
        self.project_list_widget.itemClicked.connect(self.display_project_info)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.project_list_widget)

        # Añadir el botón de crear proyecto al sidebar
        self.add_create_project_button()

        # Añadir el sidebar a una layout vertical
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(scroll_area)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)

        # Crear QDockWidget para el sidebar
        dock_widget = QDockWidget("Proyectos", self)
        dock_widget.setWidget(sidebar_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_widget)

        # Cargar proyectos existentes desde la base de datos
        self.load_projects()

        # Configurar el temporizador para actualizar los iconos GIF
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gif_icons)
        self.timer.start(100)  # Actualizar cada 100 ms

    def create_collections(self):
        # Crear colecciones si no existen
        if 'projects' not in self.db.collection_names():
            self.db.create_collection('projects')
        if 'todos' not in self.db.collection_names():
            self.db.create_collection('todos')

    def add_create_project_button(self):
        create_project_button = QPushButton("Crear Proyecto")
        create_project_button.clicked.connect(self.show_create_project_form)
        create_project_item = QListWidgetItem(self.project_list_widget)
        create_project_item.setSizeHint(create_project_button.sizeHint()) 
        self.project_list_widget.setItemWidget(create_project_item, create_project_button)

    def show_create_project_form(self):
        self.project_tab.name_input.clear()
        self.project_tab.description_input.clear()
        self.tabs.setCurrentWidget(self.project_tab)

    def load_projects(self):
        self.gif_labels = []
        projects_collection = self.db['projects']
        projects = projects_collection.find()
        for project in projects:
            description = project['description'] if len(project['description']) <= 8 else project['description'][:8] + "..."
            item = QListWidgetItem(f"{project['name']}: {description}")
            icon_path = project.get('icon_path', "assets/project_images/default_icon.png")
            
            if icon_path.endswith('.gif'):
                gif_label = GIFLabel(icon_path)
                self.gif_labels.append((item, gif_label))
                item.setIcon(QIcon(gif_label.currentPixmap()))
            else:
                item.setIcon(QIcon(icon_path))
            item.icon_path = icon_path  # Guardar la ruta del icono en el item
            self.project_list_widget.addItem(item)

    def update_gif_icons(self):
        for item, gif_label in self.gif_labels:
            item.setIcon(QIcon(gif_label.currentPixmap()))

    @Slot()
    def display_project_info(self, item):
        text = item.text()
        if text.startswith("Crear Proyecto"):
            self.show_create_project_form()
            return

        project_name, project_description = text.split(": ", 1)

        projects_collection = self.db['projects']
        project = projects_collection.find_one({"name": project_name, "description": project_description})

        if project:
            self.current_project_item = item
            self.current_project_name = project_name
            self.current_project_description = project_description
            self.current_project_info = project.get('info', '{}')
            self.current_project_id = project['_id']
            self.project_info_tab.update_project_info(project_name, project_description, self.current_project_info)
            self.project_tab.update_project_form(project_name, project_description)  # Llamar al método para actualizar el formulario

            # Actualizar el icono si está disponible
            icon_path = project.get('icon_path', "assets/project_images/default_icon.png")
            if ('.gif' in icon_path):
                gif_label = GIFLabel(icon_path)
                icon = QIcon(gif_label.currentPixmap())
            else:
                icon = QIcon(icon_path)
            self.current_project_item.setIcon(icon)

            # Actualizar el project_id en ProjectTodoTab
            self.project_todo_tab.project_id = self.current_project_id
            self.project_todo_tab.load_todos()

        else:
            self.current_project_item = item
            self.current_project_name = project_name
            self.current_project_description = project_description
            self.current_project_info = {}
            self.current_project_id = None
            self.project_info_tab.update_project_info(project_name, project_description, self.current_project_info)
            self.project_tab.update_project_form(project_name, project_description)  # Llamar al método para actualizar el formulario

        # Limpiar la búsqueda al cambiar de ítem
        self.project_info_tab.clear_search()

        self.project_tab.enable_editing()
        self.tabs.setCurrentWidget(self.project_info_tab)

    @Slot()
    def update_project_icon(self, project_name, icon_path):
        for i in range(self.project_list_widget.count()):
            item = self.project_list_widget.item(i)
            if item.text().startswith(f"{project_name}:"):
                if icon_path.endswith('.gif'):
                    gif_label = GIFLabel(icon_path)
                    self.gif_labels.append((item, gif_label))
                    item.setIcon(QIcon(gif_label.currentPixmap()))
                else:
                    item.setIcon(QIcon(icon_path))
                break

    @Slot()
    def closeEvent(self, event):
        self.client.close()
        event.accept()

    @Slot()
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            self.hide()
            self.tray_icon.showMessage(
                "Minimizado",
                "La aplicación se ha minimizado a la bandeja del sistema",
                QSystemTrayIcon.Information,
                2000
            )

    def minimize_to_tray(self):
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    print("Creando ventana principal...")
    window = MainWindow()

    print("Mostrando ventana principal...")
    window.show()

    def on_exit():
        print("Cerrando aplicación...")

    app.aboutToQuit.connect(on_exit)

    sys.exit(app.exec())
