import sys
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
                               QListWidgetItem, QHBoxLayout, QFileDialog, QTableWidget, QTableWidgetItem,
                               QHeaderView, QCompleter, QApplication)
from PySide6.QtCore import Slot, Qt
import json
from PySide6.QtGui import QIcon, QClipboard
from bson.objectid import ObjectId # Necesario si tus _id fueran ObjectIds de PyMongo y quisieras mantener esa consistencia.
                                  # Mongita por defecto usa cadenas para los _id autogenerados, lo cual es más sencillo.
                                  # Si tus IDs ya son cadenas (como de Mongita) o si las estás guardando como cadenas,
                                  # no necesitas esto. Dada tu migración, probablemente Mongita generará cadenas.


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

        self.add_info_button = QPushButton("Add")
        self.add_info_button.clicked.connect(self.add_project_info)

        self.info_form_layout.addWidget(self.info_name_input)
        self.info_form_layout.addWidget(self.info_value_input)
        self.info_form_layout.addWidget(self.add_info_button)
        layout.addLayout(self.info_form_layout)

        # Tabla para mostrar información adicional
        self.additional_info_table = QTableWidget(0, 3)
        self.additional_info_table.setHorizontalHeaderLabels(["Key", "Value", "Actions"])
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
        self.description_input.setVisible(enabled) # Corregido: Esto debería ser para el QTextEdit de descripción, no para un input de info.
                                                   # Si ya está funcionando, ignora. Parece que querías ocultar o mostrar solo para info inputs.
        self.info_value_input.setVisible(enabled)
        self.add_info_button.setVisible(enabled)
        self.edit_button.setEnabled(not enabled)  # Deshabilitar el botón de editar mientras está en modo de edición

    @Slot()
    def change_icon(self):
        icon_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Icono", "", "Imágenes (*.gif *.png *.ico *.webp)")
        if icon_path:
            self.main_window.update_project_icon(self.main_window.current_project_name, icon_path)
            projects_collection = self.main_window.db.projects

            # Usar _id para la actualización si está disponible
            if self.main_window.current_project_id:
                projects_collection.update_one(
                    {"_id": self.main_window.current_project_id},
                    {"$set": {"icon_path": icon_path}}
                )
            else:
                # Fallback si por alguna razón no hay current_project_id (aunque debería haberlo al editar)
                projects_collection.update_one(
                    {"name": self.main_window.current_project_name, "description": self.main_window.current_project_description},
                    {"$set": {"icon_path": icon_path}}
                )
            self.main_window.current_project_item.icon_path = icon_path

    @Slot()
    def save_project(self):
        project_name = self.name_input.text()
        project_description = self.description_input.toPlainText()

        if project_name and project_description:
            projects_collection = self.main_window.db.projects

            # Determinar si estamos creando un nuevo proyecto o actualizando uno existente
            if self.main_window.current_project_item is None:
                # CREAR NUEVO PROYECTO
                project_doc = {
                    "name": project_name,
                    "description": project_description,
                    "info": {}, # Información inicial vacía
                    "icon_path": "assets/project_images/default_icon.png" # Icono predeterminado
                }
                result = projects_collection.insert_one(project_doc)
                new_project_id = result.inserted_id

                # Actualizar main_window con la información del nuevo proyecto
                self.main_window.current_project_id = new_project_id
                self.main_window.current_project_name = project_name
                self.main_window.current_project_description = project_description
                self.main_window.current_project_info = {}

                # Crear un nuevo QListWidgetItem y añadirlo al sidebar
                new_project_item = QListWidgetItem()
                new_project_item.setText(f"{project_name}: {project_description[:8] + '...' if len(project_description) > 8 else project_description}")
                new_project_item.setIcon(QIcon(project_doc["icon_path"]))
                new_project_item.setData(Qt.UserRole, new_project_id) # Guardar el _id
                self.main_window.project_list_widget.addItem(new_project_item)
                self.main_window.current_project_item = new_project_item

            else:
                # ACTUALIZAR PROYECTO EXISTENTE
                # Usar el _id para asegurar que se actualice el documento correcto
                if self.main_window.current_project_id:
                    projects_collection.update_one(
                        {"_id": self.main_window.current_project_id},
                        {"$set": {
                            "name": project_name,
                            "description": project_description,
                            "info": self.main_window.current_project_info,
                            # El icon_path se actualiza en change_icon o se mantiene el existente
                            "icon_path": self.main_window.current_project_item.icon_path if hasattr(self.main_window.current_project_item, 'icon_path') else "assets/project_images/default_icon.png"
                        }}
                    )
                else:
                    # Fallback si por alguna razón el _id no está disponible (no debería ocurrir)
                    projects_collection.update_one(
                        {"name": self.main_window.current_project_name, "description": self.main_window.current_project_description},
                        {"$set": {
                            "name": project_name,
                            "description": project_description,
                            "info": self.main_window.current_project_info,
                            "icon_path": self.main_window.current_project_item.icon_path if hasattr(self.main_window.current_project_item, 'icon_path') else "assets/project_images/default_icon.png"
                        }}
                    )

            # Actualizar el texto del item en la lista del sidebar
            description = project_description if len(project_description) <= 8 else project_description[:8] + "..."
            item_text = f"{project_name}: {description}"
            self.main_window.current_project_item.setText(item_text)

            # Asegurarse de que el icono del item en la lista esté actualizado (aunque change_icon ya lo hace)
            icon_path = self.main_window.current_project_item.icon_path if hasattr(self.main_window.current_project_item, 'icon_path') else "assets/project_images/default_icon.png"
            self.main_window.update_project_icon(project_name, icon_path) # Esta función también debería usar _id para ser más robusta

            self.name_input.setReadOnly(True)
            self.description_input.setReadOnly(True)
            self.set_editing_enabled(False)  # Deshabilitar el modo de edición

    @Slot()
    def add_project_info(self):
        name = self.info_name_input.text()
        value = self.info_value_input.text()

        if name and value:
            self.main_window.current_project_info[name] = value
            self.add_info_item(name, value)

            projects_collection = self.main_window.db.projects
            # Usa _id para la actualización
            if self.main_window.current_project_id:
                projects_collection.update_one(
                    {"_id": self.main_window.current_project_id},
                    {"$set": {
                        "info": self.main_window.current_project_info
                    }}
                )
            else:
                # Fallback si no hay _id (no debería ocurrir si un proyecto está seleccionado)
                print("Advertencia: Intentando añadir info sin un current_project_id. No se guardará permanentemente.")


            self.info_name_input.clear()
            self.info_value_input.clear()

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
            self.add_info_item(key, value)

    def clear_table(self):
        self.additional_info_table.setRowCount(0)

    def add_info_item(self, key, value):
        row_position = self.additional_info_table.rowCount()
        self.additional_info_table.insertRow(row_position)

        self.additional_info_table.setItem(row_position, 0, QTableWidgetItem(key))
        self.additional_info_table.setItem(row_position, 1, QTableWidgetItem(value))

        # Botón de copiar
        copy_button = QPushButton()
        copy_button.setIcon(QIcon("assets/icons/icon_copy.png"))
        copy_button.setMaximumSize(24, 24)
        copy_button.clicked.connect(lambda: self.copy_to_clipboard(value))
        self.additional_info_table.setCellWidget(row_position, 2, copy_button)

    @Slot()
    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)