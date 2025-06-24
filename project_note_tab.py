# project_note_tab.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton,
                               QHBoxLayout, QFileDialog, QApplication, QColorDialog,
                               QFontDialog, QMessageBox, QLineEdit, QListWidget, QListWidgetItem,
                               QScrollArea, QLabel, QSplitter) # ¡Importa QSplitter!
from PySide6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from PySide6.QtCore import Slot, Qt, QDir, QFileInfo
import os
import markdown2

class ProjectNoteTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setObjectName("ProjectNoteTab")
        self.current_note_file = None
        self.project_id = None
        self.current_notes_directory = ""

        self.main_layout = QVBoxLayout(self) # Renombrar self.layout a self.main_layout para evitar conflictos

        # --- Sección de Explorador de Archivos (parte superior del splitter) ---
        # Un widget contenedor para la sección del explorador de archivos
        self.file_explorer_container = QWidget()
        self.file_explorer_layout = QVBoxLayout(self.file_explorer_container) # Usar QVBoxLayout para este contenedor
        self.file_explorer_layout.setContentsMargins(0, 0, 0, 0) # Sin márgenes extra

        self.directory_path_layout = QHBoxLayout() # Layout para la etiqueta, input y botón de examinar

        self.directory_label = QLabel("Carpeta de Notas:")
        self.directory_path_layout.addWidget(self.directory_label)

        self.directory_input = QLineEdit()
        self.directory_input.setPlaceholderText("Selecciona una carpeta para las notas del proyecto...")
        self.directory_input.setReadOnly(True)
        self.directory_path_layout.addWidget(self.directory_input)

        self.browse_button = QPushButton("Examinar...")
        self.browse_button.clicked.connect(self.browse_for_notes_directory)
        self.directory_path_layout.addWidget(self.browse_button)

        self.file_explorer_layout.addLayout(self.directory_path_layout) # Añadir el layout al contenedor principal del explorador

        # Placeholder para la lista de notas
        self.notes_placeholder_label = QLabel("Archivos de notas se listarán aquí.")
        self.notes_placeholder_label.setAlignment(Qt.AlignCenter)
        self.notes_placeholder_label.setStyleSheet("color: #888; padding: 20px; font-style: italic;")
        self.file_explorer_layout.addWidget(self.notes_placeholder_label)

        # Lista de archivos de notas
        self.notes_list_widget = QListWidget()
        self.notes_list_widget.itemClicked.connect(self.open_selected_note_from_list)
        self.notes_list_widget.setMinimumHeight(100) # Un poco más pequeña por defecto en la lista
        self.notes_list_widget.setMaximumHeight(300) # Máximo para que el editor tenga espacio
        self.file_explorer_layout.addWidget(self.notes_list_widget)

        # Ocultar la lista de notas inicialmente
        self.notes_list_widget.hide()


        # --- Sección del Editor de Texto (parte inferior del splitter) ---
        # Un widget contenedor para el editor y su toolbar
        self.editor_container = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_container)
        self.editor_layout.setContentsMargins(0, 0, 0, 0) # Sin márgenes extra

        # Barra de herramientas del editor (con Emojis)
        self.toolbar_widget = QWidget()
        self.toolbar_widget.setObjectName("NoteToolbar")
        self.toolbar_layout = QHBoxLayout(self.toolbar_widget)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar_layout.setSpacing(1)

        self.save_button = QPushButton("💾")
        self.save_button.setToolTip("Guardar Nota")
        self.save_button.clicked.connect(self.save_note)
        self.toolbar_layout.addWidget(self.save_button)

        self.load_button = QPushButton("📂")
        self.load_button.setToolTip("Cargar Nota")
        self.load_button.clicked.connect(self.load_note)
        self.toolbar_layout.addWidget(self.load_button)

        self.toolbar_layout.addStretch()

        self.bold_button = QPushButton("🅱️")
        self.bold_button.setToolTip("Negrita (Ctrl+B)")
        self.bold_button.setCheckable(True)
        self.bold_button.clicked.connect(self.toggle_bold)
        self.toolbar_layout.addWidget(self.bold_button)

        self.italic_button = QPushButton("𝐼")
        self.italic_button.setToolTip("Cursiva (Ctrl+I)")
        self.italic_button.setCheckable(True)
        self.italic_button.clicked.connect(self.toggle_italic)
        self.toolbar_layout.addWidget(self.italic_button)

        self.underline_button = QPushButton("U̲")
        self.underline_button.setToolTip("Subrayado (Ctrl+U)")
        self.underline_button.setCheckable(True)
        self.underline_button.clicked.connect(self.toggle_underline)
        self.toolbar_layout.addWidget(self.underline_button)

        self.color_button = QPushButton("🎨")
        self.color_button.setToolTip("Color de Texto")
        self.color_button.clicked.connect(self.change_text_color)
        self.toolbar_layout.addWidget(self.color_button)

        self.font_button = QPushButton("🅰️")
        self.font_button.setToolTip("Cambiar Fuente")
        self.font_button.clicked.connect(self.change_font)
        self.toolbar_layout.addWidget(self.font_button)

        self.editor_layout.addWidget(self.toolbar_widget) # Añadir toolbar al contenedor del editor

        # Editor de texto
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Escribe tus notas aquí (soporta Markdown y HTML)...")
        self.editor_layout.addWidget(self.text_editor) # Añadir editor al contenedor del editor

        # Conectar señales para actualizar el estado de los botones
        self.text_editor.selectionChanged.connect(self.update_toolbar_state)
        self.text_editor.currentCharFormatChanged.connect(self.update_toolbar_state)


        # --- Configuración del QSplitter ---
        self.splitter = QSplitter(Qt.Vertical) # Crear un splitter vertical
        self.splitter.addWidget(self.file_explorer_container) # Añadir la sección del explorador
        self.splitter.addWidget(self.editor_container)      # Añadir la sección del editor

        # Establecer tamaños iniciales. Esto es importante para que el editor sea más grande.
        # Los números son píxeles, pero son relativos al espacio disponible.
        # Por ejemplo, (150, 450) significa que la primera parte tendrá 150px y la segunda 450px.
        # Ajusta estos valores según tus preferencias.
        self.splitter.setSizes([150, 450]) # Listado (150px), Editor (450px)

        self.main_layout.addWidget(self.splitter) # Añadir el splitter al layout principal de la pestaña

        # Directorio base para notas (gestión interna)
        self.notes_base_dir = os.path.join(os.path.expanduser("~"), ".gnmau_notes")
        os.makedirs(self.notes_base_dir, exist_ok=True)

        self.update_toolbar_state() # Establece el estado inicial de los botones

    def create_separator(self):
        """No es necesario un separador si usas QSplitter, pero se puede usar para otros fines."""
        # Puedes eliminar este método si no lo usas en ninguna otra parte.
        # O dejarlo si tienes otros usos futuros.
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #555;")
        return separator

    def set_project_id(self, project_id):
        self.project_id = project_id
        self.text_editor.clear()
        self.current_note_file = None
        self.notes_list_widget.clear()

        if project_id:
            project_notes_dir = os.path.join(self.notes_base_dir, str(self.project_id))
            os.makedirs(project_notes_dir, exist_ok=True)
            self.current_notes_directory = project_notes_dir
            self.directory_input.setText(project_notes_dir)
            self.load_files_from_directory(project_notes_dir)
            self.browse_button.setEnabled(True)
        else:
            self.directory_input.clear()
            self.directory_input.setPlaceholderText("Selecciona un proyecto para gestionar notas.")
            self.browse_button.setEnabled(False)
            self.notes_list_widget.clear()
            self.show_placeholder_text("Selecciona un proyecto para gestionar notas.")

    @Slot()
    def browse_for_notes_directory(self):
        start_dir = self.current_notes_directory if self.current_notes_directory else os.path.expanduser("~")
        new_dir = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Notas", start_dir)
        if new_dir:
            self.current_notes_directory = new_dir
            self.directory_input.setText(new_dir)
            self.load_files_from_directory(new_dir)
            self.main_window.update_project_notes_folder(self.project_id, new_dir)

    def load_files_from_directory(self, directory_path):
        self.notes_list_widget.clear()
        
        if not os.path.isdir(directory_path):
            self.show_placeholder_text("La carpeta seleccionada no existe o no es válida.")
            return

        supported_extensions = ('.txt', '.html', '.htm', '.md', '.markdown')
        found_files = []
        for filename in os.listdir(directory_path):
            if filename.lower().endswith(supported_extensions):
                filepath = os.path.join(directory_path, filename)
                found_files.append((filename, filepath))
        
        if found_files:
            self.notes_placeholder_label.hide()
            self.notes_list_widget.show()
            for filename, filepath in found_files:
                item = QListWidgetItem(filename)
                item.setData(Qt.UserRole, filepath)
                self.notes_list_widget.addItem(item)
        else:
            self.show_placeholder_text("No hay archivos de notas en esta carpeta.")
            self.notes_list_widget.hide()

    def show_placeholder_text(self, text):
        self.notes_placeholder_label.setText(text)
        self.notes_placeholder_label.show()
        self.notes_list_widget.hide()

    @Slot()
    def open_selected_note_from_list(self, item):
        file_path = item.data(Qt.UserRole)
        if file_path:
            self._load_file_into_editor(file_path)

    def _load_file_into_editor(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors='ignore') as f:
                content = f.read()
                if filepath.lower().endswith(('.md', '.markdown')):
                    html_content = markdown2.markdown(content, extras=["fenced-code-blocks", "tables", "strike", "code-friendly"])
                    self.text_editor.setHtml(html_content)
                elif filepath.lower().endswith(('.html', '.htm')):
                    self.text_editor.setHtml(content)
                else:
                    self.text_editor.setPlainText(content)
            self.current_note_file = filepath
        except Exception as e:
            QMessageBox.critical(self, "Error al Cargar", f"No se pudo cargar la nota '{os.path.basename(filepath)}': {e}")

    @Slot()
    def toggle_bold(self):
        cursor = self.text_editor.textCursor()
        fmt = cursor.charFormat()
        new_weight = QFont.Normal if fmt.fontWeight() == QFont.Bold else QFont.Bold
        fmt.setFontWeight(new_weight)
        cursor.mergeCharFormat(fmt)
        self.text_editor.setCurrentCharFormat(fmt)

    @Slot()
    def toggle_italic(self):
        cursor = self.text_editor.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        cursor.mergeCharFormat(fmt)
        self.text_editor.setCurrentCharFormat(fmt)

    @Slot()
    def toggle_underline(self):
        cursor = self.text_editor.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        cursor.mergeCharFormat(fmt)
        self.text_editor.setCurrentCharFormat(fmt)

    @Slot()
    def change_text_color(self):
        current_color = self.text_editor.textColor()
        color = QColorDialog.getColor(current_color, self, "Seleccionar Color de Texto")
        if color.isValid():
            cursor = self.text_editor.textCursor()
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            cursor.mergeCharFormat(fmt)
            self.text_editor.setCurrentCharFormat(fmt)

    @Slot()
    def change_font(self):
        font, ok = QFontDialog.getFont(self.text_editor.font(), self, "Seleccionar Fuente")
        if ok:
            cursor = self.text_editor.textCursor()
            fmt = QTextCharFormat()
            fmt.setFont(font)
            cursor.mergeCharFormat(fmt)
            self.text_editor.setCurrentCharFormat(fmt)

    @Slot()
    def update_toolbar_state(self):
        current_format = self.text_editor.currentCharFormat()
        self.bold_button.setChecked(current_format.fontWeight() == QFont.Bold)
        self.italic_button.setChecked(current_format.fontItalic())
        self.underline_button.setChecked(current_format.fontUnderline())

    @Slot()
    def save_note(self):
        if not self.project_id:
            QMessageBox.warning(self, "Guardar Nota", "Selecciona o crea un proyecto antes de guardar una nota.")
            return

        initial_save_dir = self.current_notes_directory
        if not os.path.exists(initial_save_dir):
            initial_save_dir = os.path.join(self.notes_base_dir, str(self.project_id))
            os.makedirs(initial_save_dir, exist_ok=True)

        if self.current_note_file and os.path.exists(os.path.dirname(self.current_note_file)):
            initial_save_dir = os.path.dirname(self.current_note_file)

        suggested_filename = self.current_note_file if self.current_note_file else f"{self.main_window.current_project_name}_nota.html"

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Guardar Nota",
            suggested_filename,
            "Archivos HTML (*.html);;Archivos Markdown (*.md);;Archivos de Texto (*.txt);;Todos los archivos (*)"
        )
        if not filepath:
            return

        try:
            if filepath.lower().endswith(('.md', '.markdown')):
                content_to_save = self.text_editor.toPlainText()
            else:
                content_to_save = self.text_editor.toHtml() if filepath.lower().endswith(('.html', '.htm')) else self.text_editor.toPlainText()

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content_to_save)

            self.current_note_file = filepath
            QMessageBox.information(self, "Guardar Nota", f"Nota guardada exitosamente en:\n{filepath}")
            
            self.load_files_from_directory(os.path.dirname(filepath))

        except Exception as e:
            QMessageBox.critical(self, "Error al Guardar", f"No se pudo guardar la nota: {e}")

    @Slot()
    def load_note(self):
        if not self.project_id:
            QMessageBox.warning(self, "Cargar Nota", "Selecciona un proyecto para cargar sus notas.")
            return

        start_dir = self.current_notes_directory if self.current_notes_directory else os.path.expanduser("~")
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Cargar Nota",
            start_dir,
            "Archivos de Nota (*.html *.md *.txt);;Archivos HTML (*.html);;Archivos Markdown (*.md);;Archivos de Texto (*.txt);;Todos los archivos (*)"
        )
        if filepath:
            self._load_file_into_editor(filepath)