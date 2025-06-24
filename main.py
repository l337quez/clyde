import sys
import os
# from pymongo import MongoClient # Comentada o eliminada en la revisión anterior
from mongita import MongitaClientDisk # Importada en la revisión anterior
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget,
                               QWidget, QVBoxLayout, QSystemTrayIcon,
                               QMenu, QListWidget, QScrollArea, QLabel,
                               QDockWidget, QListWidgetItem, QPushButton)
from PySide6.QtGui import QIcon, QAction, QPixmap, QMovie
from PySide6.QtCore import Slot, Qt, QEvent, QTimer
from project_tab import ProjectTab
from project_info_tab import ProjectInfoTab
from project_todo_tab import ProjectTodoTab
from project_note_tab import ProjectNoteTab
from about_tab import AboutTab
from setting_tab import SettingTab
from icon import icon
from PySide6.QtWidgets import QSizePolicy
import json
from dotenv import load_dotenv

# load env file
load_dotenv()

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

        self.config_path = os.path.join(os.path.expanduser("~"), ".myapp", "config.json")
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        self.config = {}
        self.load_config()

        qp = QPixmap()
        qp.loadFromData(icon)
        appIcon = QIcon(qp)
        self.setWindowIcon(appIcon)

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

        self.current_project_name = ""
        self.current_project_description = ""
        self.current_project_item = None
        self.current_project_info = {}
        self.current_project_id = "default_project_id" # Se actualiza cuando se selecciona un proyecto o se crea uno nuevo
        self.db_name = "projects_db"

        print("Conectando a Mongita...")
        mongita_db_dir = os.path.join(os.path.dirname(__file__), "mongita_data")
        os.environ["MONGITA_DIR"] = mongita_db_dir
        self.client = MongitaClientDisk(mongita_db_dir)
        self.db = self.client[self.db_name]

        print("Conectando a MongoDB...") # Este mensaje ahora se refiere a Mongita
        self.create_collections()

        if self.db.projects.count_documents({}) == 0:
            print("Insertando un proyecto de prueba en Mongita...")
            self.db.projects.insert_one({
                "name": "Proyecto Demo",
                "description": "Este es un proyecto de prueba.",
                "icon_path": "assets/project_images/default_icon.png"
            })

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.project_tab = ProjectTab(self)
        self.project_info_tab = ProjectInfoTab(self)
        # Asegurarse de que project_id se actualice correctamente en display_project_info
        self.project_todo_tab = ProjectTodoTab(self, project_id=self.current_project_id)
        self.project_note_tab = ProjectNoteTab(self)
        self.setting_tab = SettingTab(self)
        self.about_tab = AboutTab(self)
        self.tabs.addTab(self.project_tab, "Project")
        self.tabs.addTab(self.project_info_tab, "Information")
        self.tabs.addTab(self.project_todo_tab, "Todo")
        self.tabs.addTab(self.project_note_tab, "Note")
        self.tabs.addTab(self.setting_tab, "Setting")
        self.tabs.addTab(self.about_tab, "About")

        self.project_list_widget = QListWidget()
        self.project_list_widget.itemClicked.connect(self.display_project_info)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.project_list_widget)

        self.add_create_project_button()

        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(scroll_area)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)

        self.dock_widget = QDockWidget("Projects", self)
        self.dock_widget.setWidget(sidebar_widget)
        self.dock_widget.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)

        self.load_projects()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gif_icons)
        self.timer.start(100)

        dock_position_int = self.config.get("sidebar_position", Qt.LeftDockWidgetArea.value)
        dock_position = Qt.DockWidgetArea(dock_position_int)
        self.addDockWidget(dock_position, self.dock_widget)

        self.dock_widget.dockLocationChanged.connect(self.save_sidebar_position)

    def save_sidebar_position(self):
        position = self.dockWidgetArea(self.dock_widget)
        self.config["sidebar_position"] = int(position)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            dark_mode = self.config.get("dark_mode", False)
            self.apply_theme(dark_mode)

    def apply_theme(self, dark_mode):
        if dark_mode:
            with open("dark_theme.qss", "r") as f:
                dark_style_sheet = f.read()
            self.setStyleSheet(dark_style_sheet)
        else:
            self.setStyleSheet("")

    def create_collections(self):
        # Mongita crea las colecciones automáticamente al insertar el primer documento.
        # Estas llamadas a create_collection son inofensivas pero no estrictamente necesarias
        # para el funcionamiento de Mongita. Se mantienen solo para consistencia si se desea.
        if 'projects' not in self.db.list_collection_names():
            print("Mongita: Colección 'projects' creada automáticamente al primer insert.")
            # self.db.create_collection('projects') # No es necesario para Mongita
        if 'todos' not in self.db.list_collection_names():
            print("Mongita: Colección 'todos' creada automáticamente al primer insert.")
            # self.db.create_collection('todos') # No es necesario para Mongita

    def add_create_project_button(self):
        create_project_button = QPushButton("Create Project")
        create_project_button.setStyleSheet("padding: 4px; margin: 8px;")
        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        create_project_button.setSizePolicy(size_policy)
        create_project_button.clicked.connect(self.show_create_project_form)
        
        create_project_item = QListWidgetItem(self.project_list_widget)
        create_project_item.setSizeHint(create_project_button.sizeHint())
        # --- CAMBIO AQUI: Marcar el item para que display_project_info lo ignore ---
        create_project_item.setData(Qt.UserRole, None) # O un valor distintivo como "CREATE_NEW_PROJECT_ID"
        # --- FIN DEL CAMBIO ---
        self.project_list_widget.setItemWidget(create_project_item, create_project_button)

    def show_create_project_form(self):
        self.current_project_item = None
        self.current_project_name = ""
        self.current_project_description = ""
        self.current_project_info = {}
        self.current_project_id = None # Reiniciar el ID para indicar un nuevo proyecto
        self.project_tab.name_input.clear()
        self.project_tab.description_input.clear()
        self.project_tab.clear_table() # Limpiar tabla de info adicional al crear uno nuevo
        self.project_tab.set_editing_enabled(True) # Habilitar edición para nuevo proyecto
        self.tabs.setCurrentWidget(self.project_tab)

    def load_projects(self):
        self.gif_labels = []
        projects_collection = self.db.projects
        projects = projects_collection.find()
        # Limpiar la lista existente antes de cargar nuevos proyectos
        self.project_list_widget.clear()
        self.add_create_project_button() # Volver a añadir el botón "Create Project"
        for project in projects:
            description = project['description'] if len(project['description']) <= 8 else project['description'][:8] + "..."
            item = QListWidgetItem(f"{project['name']}: {description}")
            item.setData(Qt.UserRole, project["_id"]) # Asegúrate de almacenar el _id
            icon_path = project.get('icon_path', "assets/project_images/default_icon.png")

            if icon_path.endswith('.gif'):
                gif_label = GIFLabel(icon_path)
                self.gif_labels.append((item, gif_label))
                item.setIcon(QIcon(gif_label.currentPixmap()))
            else:
                item.setIcon(QIcon(icon_path))
            item.icon_path = icon_path
            self.project_list_widget.addItem(item)

    def update_gif_icons(self):
        for item, gif_label in self.gif_labels:
            item.setIcon(QIcon(gif_label.currentPixmap()))

    @Slot()
    def display_project_info(self, item):
        # --- CAMBIO AQUI: Manejar el clic en el botón "Create Project" ---
        project_id = item.data(Qt.UserRole)
        if project_id is None: # Si el item no tiene un ID de proyecto válido
            self.show_create_project_form()
            return # Salir de la función
        # --- FIN DEL CAMBIO ---

        project = self.db.projects.find_one({"_id": project_id})
        if not project:
            print("No se encontró ningún documento con ese _id:", project_id)
            # Opcional: podrías remover el item de la lista si el proyecto ya no existe en la DB
            # self.project_list_widget.takeItem(self.project_list_widget.row(item))
            return

        self.current_project_item = item
        self.current_project_id = project_id
        self.current_project_name = project["name"]
        self.current_project_description = project["description"]
        self.current_project_info = project.get("info", {})

        self.project_info_tab.update_project_info(
            self.current_project_name,
            self.current_project_description,
            self.current_project_info
        )
        self.project_tab.update_project_form(
            self.current_project_name,
            self.current_project_description
        )

        icon_path = project.get('icon_path', "assets/project_images/default_icon.png")
        if icon_path.endswith('.gif'):
            gif_label = GIFLabel(icon_path)
            icon = QIcon(gif_label.currentPixmap())
        else:
            icon = QIcon(icon_path)
        self.current_project_item.setIcon(icon)

        self.project_todo_tab.project_id = self.current_project_id
        self.project_todo_tab.load_todos()

        self.project_info_tab.clear_search()
        self.project_tab.enable_editing()
        self.tabs.setCurrentWidget(self.project_info_tab)

    @Slot()
    def update_project_icon(self, project_name, icon_path):
        # Es más robusto buscar por _id, pero si project_name es único, puede funcionar.
        # Se asume que el project_name en este contexto corresponde al current_project_name
        # del proyecto actualmente seleccionado.
        if self.current_project_id:
            for i in range(self.project_list_widget.count()):
                item = self.project_list_widget.item(i)
                if item.data(Qt.UserRole) == self.current_project_id:
                    if icon_path.endswith('.gif'):
                        # Asegurarse de que el GIFLabel sea el correcto o crear uno nuevo si es necesario
                        found = False
                        for idx, (existing_item, existing_gif_label) in enumerate(self.gif_labels):
                            if existing_item == item:
                                existing_gif_label = GIFLabel(icon_path) # Recrear para la nueva ruta
                                self.gif_labels[idx] = (item, existing_gif_label)
                                item.setIcon(QIcon(existing_gif_label.currentPixmap()))
                                found = True
                                break
                        if not found: # Si no se encontró en gif_labels, añadirlo
                            gif_label = GIFLabel(icon_path)
                            self.gif_labels.append((item, gif_label))
                            item.setIcon(QIcon(gif_label.currentPixmap()))
                    else:
                        item.setIcon(QIcon(icon_path))
                    item.icon_path = icon_path # Actualizar la ruta en el item
                    break


    @Slot()
    def closeEvent(self, event):
        # Aunque Mongita no lo requiere tan estrictamente como PyMongo, es buena práctica.
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