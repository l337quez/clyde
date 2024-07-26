import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QCheckBox, QScrollArea, QDialog, QDialogButtonBox)
from PySide6.QtCore import Slot, Qt

class ProjectTodoTab(QWidget):
    def __init__(self, main_window, project_id):
        super().__init__()
        self.main_window = main_window
        self.project_id = project_id
        self.layout = QVBoxLayout(self)

        # Botón para añadir nueva tarea
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.open_add_dialog)
        self.layout.addWidget(self.add_button)

        # Área de scroll para mostrar las tareas
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.todo_list_widget = QWidget()
        self.todo_list_layout = QVBoxLayout(self.todo_list_widget)
        self.scroll_area.setWidget(self.todo_list_widget)
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

        # Cargar tareas desde la base de datos
        self.load_todos()

    def load_todos(self):
        todos_collection = self.main_window.db.todos
        todos = todos_collection.find({"project_id": self.project_id})
        for todo in todos:
            title, description, tasks = todo['title'], todo['description'], todo['tasks']
            self.add_todo_item(title, description, tasks, False)

    def update_project_id(self, project_id):
        self.project_id = project_id
        self.load_todos()

    def add_todo_item(self, title, description, tasks, new):
        todo_widget = QWidget()
        todo_layout = QVBoxLayout()

        title_label = QLabel(f"<b>{title}</b>")
        description_label = QLabel(description)

        title_layout = QHBoxLayout()
        title_layout.addWidget(title_label)
        check_button = QCheckBox()
        title_layout.addWidget(check_button)
        todo_layout.addLayout(title_layout)
        todo_layout.addWidget(description_label)

        tasks_layout = QVBoxLayout()
        for task in tasks:
            task_layout = QHBoxLayout()
            task_check = QCheckBox(task['task'])
            task_check.setChecked(task['checked'])
            task_check.stateChanged.connect(self.update_task_state)
            task_layout.addWidget(task_check)
            tasks_layout.addLayout(task_layout)

        todo_layout.addLayout(tasks_layout)
        todo_widget.setLayout(todo_layout)
        self.todo_list_layout.addWidget(todo_widget)

        check_button.stateChanged.connect(lambda state, w=todo_widget: self.update_main_task_state(state, w, tasks_layout))

        if new:
            self.save_todo_to_db(title, description, tasks)

    @Slot()
    def open_add_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Todo")
        dialog_layout = QVBoxLayout(dialog)

        title_input = QLineEdit()
        title_input.setPlaceholderText("Title")
        description_input = QTextEdit()
        description_input.setPlaceholderText("Description")
        task_input = QLineEdit()
        task_input.setPlaceholderText("Task (comma separated)")

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_todo_from_dialog(dialog, title_input, description_input, task_input))
        button_box.rejected.connect(dialog.reject)

        dialog_layout.addWidget(title_input)
        dialog_layout.addWidget(description_input)
        dialog_layout.addWidget(task_input)
        dialog_layout.addWidget(button_box)

        dialog.setLayout(dialog_layout)
        dialog.exec()

    def add_todo_from_dialog(self, dialog, title_input, description_input, task_input):
        title = title_input.text()
        description = description_input.toPlainText()
        tasks = [{'task': task.strip(), 'checked': False} for task in task_input.text().split(',')]

        self.add_todo_item(title, description, tasks, True)
        dialog.accept()

    def save_todo_to_db(self, title, description, tasks):
        todos_collection = self.main_window.db.todos
        todos_collection.insert_one({
            "title": title,
            "description": description,
            "tasks": tasks,
            "project_id": self.project_id
        })

    @Slot()
    def update_task_state(self, state):
        parent_widget = self.sender().parentWidget().parentWidget()
        for i in range(parent_widget.layout().count()):
            task_layout = parent_widget.layout().itemAt(i).layout()
            for j in range(task_layout.count()):
                task_check = task_layout.itemAt(j).widget()
                if isinstance(task_check, QCheckBox):
                    if not task_check.isChecked():
                        parent_widget.parentWidget().layout().itemAt(1).widget().setChecked(False)
                        return
        parent_widget.parentWidget().layout().itemAt(1).widget().setChecked(True)

    @Slot()
    def update_main_task_state(self, state, widget, tasks_layout):
        if state == Qt.Checked:
            for i in range(tasks_layout.count()):
                task_layout = tasks_layout.itemAt(i).layout()
                for j in range(task_layout.count()):
                    task_check = task_layout.itemAt(j).widget()
                    if isinstance(task_check, QCheckBox):
                        task_check.setChecked(True)
        else:
            for i in range(tasks_layout.count()):
                task_layout = tasks_layout.itemAt(i).layout()
                for j in range(task_layout.count()):
                    task_check = task_layout.itemAt(j).widget()
                    if isinstance(task_check, QCheckBox):
                        task_check.setChecked(False)
        self.save_all_todos_to_db()

    def save_all_todos_to_db(self):
        todos = []
        for i in range(self.todo_list_layout.count()):
            widget = self.todo_list_layout.itemAt(i).widget()
            title = widget.layout().itemAt(0).layout().itemAt(0).widget().text()
            description = widget.layout().itemAt(1).widget().text()
            tasks = []
            tasks_layout = widget.layout().itemAt(2)
            for j in range(tasks_layout.count()):
                task_layout = tasks_layout.itemAt(j).layout()
                for k in range(task_layout.count()):
                    task_check = task_layout.itemAt(k).widget()
                    if isinstance(task_check, QCheckBox):
                        tasks.append({'task': task_check.text(), 'checked': task_check.isChecked()})
            todos.append((title, description, tasks))
        
        todos_collection = self.main_window.db.todos
        todos_collection.delete_many({"project_id": self.project_id})
        for todo in todos:
            todos_collection.insert_one({
                "title": todo[0],
                "description": todo[1],
                "tasks": todo[2],
                "project_id": self.project_id
            })
