from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QScrollArea, 
                               QCompleter, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QHBoxLayout, QApplication, QFileDialog )
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QIcon, QClipboard
import json
from tag_widget import TagWidget  # Asegúrate de importar el nuevo widget

class ProjectInfoTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.info_layout = QVBoxLayout()

        self.project_name_label = QLabel("Nombre del Proyecto")
        self.info_layout.addWidget(self.project_name_label)
        
        self.project_description_label = QLabel("Descripción del Proyecto")
        self.info_layout.addWidget(self.project_description_label)

        # Layout para botones de editar y cambiar icono
        buttons_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by key")
        self.search_input.returnPressed.connect(self.search_info)
        buttons_layout.addWidget(self.search_input)
        self.info_layout.addLayout(buttons_layout)

        #on_tag_text_edited
        # Inputs para añadir nueva información
        self.info_form_layout = QHBoxLayout()
        self.info_name_input = QLineEdit()
        self.info_name_input.setPlaceholderText("key")
        self.info_value_input = QLineEdit()
        self.info_value_input.setPlaceholderText("value")
        self.info_tag_input = QLineEdit()
        self.info_tag_input.setPlaceholderText("tags (comma separated)")

        # Configurar el autocompletado de tags
        self.add_info_button = QPushButton("Add")
        self.add_info_button.clicked.connect(self.add_project_info)
        
        self.info_form_layout.addWidget(self.info_name_input)
        self.info_form_layout.addWidget(self.info_value_input)
        self.info_form_layout.addWidget(self.info_tag_input)
        self.info_form_layout.addWidget(self.add_info_button)
        self.info_layout.addLayout(self.info_form_layout)

        # Tabla para mostrar información adicional
        self.additional_info_table = QTableWidget(0, 4)
        self.additional_info_table.setHorizontalHeaderLabels(["Key", "Value", "Tags", "Actions"])
        self.additional_info_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.additional_info_table.setAlternatingRowColors(True)
        self.additional_info_table.verticalHeader().setVisible(False)  # Ocultar la numeración de las filas

        self.info_layout.addWidget(self.additional_info_table)

        self.setLayout(self.info_layout)
        self.set_editing_enabled(False)

    def update_project_info(self, name, description, info, tags):
        self.project_name_label.setText(f"Nombre: {name}")
        self.project_description_label.setText(f"Descripción: {description}")
        self.clear_table()
        info_dict = json.loads(info) if isinstance(info, str) else info
        for key, value in info_dict.items():
            self.add_info_item(key, value, tags)

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
    def enable_editing(self):
        self.set_editing_enabled(True)

    def set_editing_enabled(self, enabled):
        self.info_name_input.setVisible(enabled)
        self.info_value_input.setVisible(enabled)
        self.info_tag_input.setVisible(enabled)
        self.add_info_button.setVisible(enabled)

    @Slot()
    def search_info(self):
        search_key = self.search_input.text().lower()
        for row in range(self.additional_info_table.rowCount()):
            item = self.additional_info_table.item(row, 0)  # Buscar en la columna de keys
            if item and search_key in item.text().lower():
                self.additional_info_table.showRow(row)
            else:
                self.additional_info_table.hideRow(row)

    @Slot()
    def clear_search(self):
        self.search_input.clear()
        for row in range(self.additional_info_table.rowCount()):
            self.additional_info_table.showRow(row)

    @Slot()
    def change_icon(self):

        icon_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Icono", "", "Imágenes PNG (*.png);;Imágenes GIF (*.gif)")
        if icon_path:
            self.main_window.current_project_item.setIcon(QIcon(icon_path))
            projects_collection = self.main_window.db.projects
            print(icon_path)
            print(projects_collection)
            print(self.main_window.current_project_name)
            result=projects_collection.update_one(
                {"name": self.main_window.current_project_name, "description": self.main_window.current_project_description},
                {"$set": {"icon_path": icon_path}}
            )       
            print(f"Icon path updated: {result.modified_count} document(s) modified.")     


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



    