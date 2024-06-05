from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, 
                               QListWidgetItem, QHBoxLayout, QFileDialog, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QCompleter, QApplication)
from PySide6.QtCore import Slot, Qt
import json
from PySide6.QtGui import QIcon, QClipboard

from tag_widget import TagWidget 



class ProjectTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        # Crear input para el nombre del proyecto
        name_label = QLabel("Nombre del Proyecto")
        self.name_input = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        # Crear input para la descripción del proyecto
        description_label = QLabel("Descripción del Proyecto")
        self.description_input = QTextEdit()
        layout.addWidget(description_label)
        layout.addWidget(self.description_input)

        # Layout para botones de guardar, editar, y cambiar icono
        buttons_layout = QHBoxLayout()
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.enable_editing)
        self.change_icon_button = QPushButton("Change Icon")
        self.change_icon_button.clicked.connect(self.change_icon)
        save_button = QPushButton("Guardar Proyecto")
        save_button.clicked.connect(self.save_project)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.change_icon_button)
        buttons_layout.addWidget(save_button)
        layout.addLayout(buttons_layout)

        # Inputs para añadir nueva información
        self.info_form_layout = QHBoxLayout()
        self.info_name_input = QLineEdit()
        self.info_name_input.setPlaceholderText("key")
        self.info_value_input = QLineEdit()
        self.info_value_input.setPlaceholderText("value")
        self.info_tag_input = QLineEdit()
        self.info_tag_input.setPlaceholderText("tags (comma separated)")

        # Configurar el autocompletado de tags
        self.tags = [
            'github', 'bitbucket', 'gitlab', 'digital ocean', 'aws', 'aws s3', 
            'email', 'ssh', 'docker', 'kubernetes', 'heroku', 'netlify', 
            'azure', 'gcp', 'firebase', 'postman', 'slack', 'trello', 'jira'
        ]
        self.tag_completer = QCompleter(self.tags)
        self.tag_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.tag_completer.setWrapAround(False)
        self.info_tag_input.setCompleter(self.tag_completer)
        self.info_tag_input.textEdited.connect(self.on_tag_text_edited)

        self.add_info_button = QPushButton("Add")
        self.add_info_button.clicked.connect(self.add_project_info)

        self.info_form_layout.addWidget(self.info_name_input)
        self.info_form_layout.addWidget(self.info_value_input)
        self.info_form_layout.addWidget(self.info_tag_input)
        self.info_form_layout.addWidget(self.add_info_button)
        layout.addLayout(self.info_form_layout)

        # Tabla para mostrar información adicional
        self.additional_info_table = QTableWidget(0, 4)
        self.additional_info_table.setHorizontalHeaderLabels(["Key", "Value", "Tags", "Actions"])
        self.additional_info_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.additional_info_table.setAlternatingRowColors(True)
        self.additional_info_table.verticalHeader().setVisible(False)  # Ocultar la numeración de las filas

        layout.addWidget(self.additional_info_table)

        self.setLayout(layout)
        self.set_editing_enabled(False)

    @Slot()
    def enable_editing(self):
        self.name_input.setReadOnly(False)
        self.description_input.setReadOnly(False)
        self.set_editing_enabled(True)

    def set_editing_enabled(self, enabled):
        self.info_name_input.setVisible(enabled)
        self.description_input.setVisible(enabled)
        self.info_value_input.setVisible(enabled)
        self.info_tag_input.setVisible(enabled)
        self.add_info_button.setVisible(enabled)

    @Slot()
    def change_icon(self):
        icon_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Icono", "", "Imágenes (*.gif *.png *.ico)")
        if icon_path:
            self.main_window.update_project_icon(self.main_window.current_project_name, icon_path)
            projects_collection = self.main_window.db.projects
            projects_collection.update_one(
                {"name": self.main_window.current_project_name, "description": self.main_window.current_project_description},
                {"$set": {"icon_path": icon_path}}
            )
            self.main_window.current_project_item.icon_path = icon_path 

    @Slot()
    def enable_editing(self):
        self.name_input.setReadOnly(False)
        self.description_input.setReadOnly(False)
        self.set_editing_enabled(True)

    def set_editing_enabled(self, enabled):
        self.info_name_input.setVisible(enabled)
        self.info_value_input.setVisible(enabled)
        self.info_tag_input.setVisible(enabled)
        self.add_info_button.setVisible(enabled)
        self.edit_button.setEnabled(not enabled)  # Deshabilitar el botón de editar mientras está en modo de edición

    @Slot()
    def save_project(self):
        project_name = self.name_input.text()
        project_description = self.description_input.toPlainText()

        if project_name and project_description:
            projects_collection = self.main_window.db.projects

            # Verificar si es un nuevo proyecto
            if self.main_window.current_project_item is None:
                # Crear un nuevo QListWidgetItem
                new_project_item = QListWidgetItem()
                new_project_item.setText(f"{project_name}: {project_description[:8] + '...' if len(project_description) > 8 else project_description}")
                new_project_item.setIcon(QIcon("default_icon.png"))  # Establecer un ícono predeterminado

                # Añadir el nuevo proyecto al QListWidget de la ventana principal
                self.main_window.project_list_widget.addItem(new_project_item)

                # Establecer el nuevo proyecto como el proyecto actual
                self.main_window.current_project_item = new_project_item
                self.main_window.current_project_name = project_name
                self.main_window.current_project_description = project_description
                self.main_window.current_project_info = {}
                self.main_window.current_project_tags = []

            icon = self.main_window.current_project_item.icon()
            if not icon.isNull():
                pixmap = icon.pixmap(24, 24)  # Tamaño del icono
                icon_path = self.main_window.current_project_item.icon_path if hasattr(self.main_window.current_project_item, 'icon_path') else "default_icon.png"
            else:
                icon_path = "default_icon.png"

            projects_collection.update_one(
                {"name": self.main_window.current_project_name},
                {"$set": {
                    "name": project_name,
                    "description": project_description,
                    "info": json.dumps(self.main_window.current_project_info),
                    "tags": self.main_window.current_project_tags,
                    "icon_path": icon_path
                }},
                upsert=True
            )

            description = project_description if len(project_description) <= 8 else project_description[:8] + "..."
            item_text = f"{project_name}: {description}"
            self.main_window.current_project_item.setText(item_text)
            self.main_window.update_project_icon(project_name, icon_path)  # Update the project icon

            self.name_input.setReadOnly(True)
            self.description_input.setReadOnly(True)
            self.set_editing_enabled(False)  # Deshabilitar el modo de edición



    @Slot()
    def add_project_info(self):
        name = self.info_name_input.text()
        value = self.info_value_input.text()
        tags = [tag.strip() for tag in self.info_tag_input.text().split(',')]

        if name and value:
            self.main_window.current_project_info[name] = value
            self.main_window.current_project_tags.extend(tags)
            self.add_info_item(name, value, tags)

            projects_collection = self.main_window.db.projects
            projects_collection.update_one(
                {"name": self.main_window.current_project_name, "description": self.main_window.current_project_description},
                {"$set": {
                    "info": json.dumps(self.main_window.current_project_info),  # Guardar como cadena JSON
                    "tags": self.main_window.current_project_tags
                }}
            )

            self.info_name_input.clear()
            self.info_value_input.clear()
            self.info_tag_input.clear()

    def update_project_form(self, name, description):
        self.name_input.setText(name)
        self.description_input.setText(description)
        self.name_input.setReadOnly(True)
        self.description_input.setReadOnly(True)
        self.update_additional_info_table()

    def update_additional_info_table(self):
        self.clear_table()
        info_dict = self.main_window.current_project_info
        for key, value in info_dict.items():
            self.add_info_item(key, value, self.main_window.current_project_tags)

    def clear_table(self):
        self.additional_info_table.setRowCount(0)

    def add_info_item(self, key, value, tags):
        row_position = self.additional_info_table.rowCount()
        self.additional_info_table.insertRow(row_position)

        self.additional_info_table.setItem(row_position, 0, QTableWidgetItem(key))
        self.additional_info_table.setItem(row_position, 1, QTableWidgetItem(value))

        # Crear un widget para contener los tags
        tags_widget = QWidget()
        tags_layout = QHBoxLayout()
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(1)
        tags_widget.setLayout(tags_layout)

        for tag in tags:
            tag_widget = TagWidget(tag)
            tags_layout.addWidget(tag_widget)

        tags_layout.addStretch()  # Para que no estire el contenido

        self.additional_info_table.setCellWidget(row_position, 2, tags_widget)

        # Botón de copiar
        copy_button = QPushButton()
        copy_button.setIcon(QIcon("icon_copiar.png"))
        copy_button.setMaximumSize(24, 24)
        copy_button.clicked.connect(lambda: self.copy_to_clipboard(value))
        self.additional_info_table.setCellWidget(row_position, 3, copy_button)

    @Slot()
    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    @Slot()
    def on_tag_text_edited(self, text):
        cursor_position = self.info_tag_input.cursorPosition()
        text_before_cursor = text[:cursor_position]
        last_comma_position = text_before_cursor.rfind(',')
        if last_comma_position == -1:
            self.tag_completer.setCompletionPrefix(text_before_cursor.strip())
        else:
            self.tag_completer.setCompletionPrefix(text_before_cursor[last_comma_position + 1:].strip())
        self.tag_completer.complete()
