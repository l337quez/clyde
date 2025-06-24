from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QScrollArea,
    QLineEdit, QTextEdit, QDialog, QDialogButtonBox
)
from bson.objectid import ObjectId
from todo_item_widget import TodoItemWidget


class ProjectTodoTab(QWidget):
    def __init__(self, main_window, project_id):
        super().__init__()
        self.main_window = main_window
        self.project_id = project_id
        self.todos_collection = self.main_window.db.todos

        self.layout = QVBoxLayout(self)

        # Scroll area for ToDo items
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.todos_container = QWidget()
        self.todos_layout = QVBoxLayout(self.todos_container)
        self.scroll_area.setWidget(self.todos_container)
        self.layout.addWidget(self.scroll_area)

        # Add new todo button
        self.add_button = QPushButton("➕ New To-Do")
        self.add_button.clicked.connect(self.show_add_todo_dialog)
        self.layout.addWidget(self.add_button)

        self.load_todos()

    def load_todos(self):
        # Clear old items
        for i in reversed(range(self.todos_layout.count())):
            self.todos_layout.itemAt(i).widget().setParent(None)

        todos = self.todos_collection.find({"project_id": str(self.project_id)})
        for todo in todos:
            widget = TodoItemWidget(
                title=todo["title"],
                description=todo["description"],
                tasks=todo["tasks"],
                on_delete=lambda w, _id=todo["_id"]: self.delete_todo(w, _id),
                on_update=lambda w, _id=todo["_id"]: self.update_todo(w, _id)
            )
            self.todos_layout.addWidget(widget)

    def show_add_todo_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("New To-Do")
        layout = QVBoxLayout(dialog)

        title_input = QLineEdit()
        title_input.setPlaceholderText("Title")
        layout.addWidget(title_input)

        description_input = QTextEdit()
        description_input.setPlaceholderText("Description (optional)")
        layout.addWidget(description_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(lambda: self.create_todo(dialog, title_input.text(), description_input.toPlainText()))
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def create_todo(self, dialog, title, description):
        if not title.strip():
            return
        new_todo = {
            "title": title.strip(),
            "description": description.strip(),
            "tasks": [],
            "project_id": str(self.project_id),
        }
        self.todos_collection.insert_one(new_todo)
        dialog.accept()
        self.load_todos()

    def delete_todo(self, widget, todo_id):
        self.todos_collection.delete_one({"_id": ObjectId(todo_id)})
        widget.setParent(None)

    def update_todo(self, widget, todo_id):
        data = widget.get_data()
        self.todos_collection.update_one(
            {"_id": ObjectId(todo_id)},
            {"$set": {
                "title": data["title"],
                "description": data["description"],
                "tasks": data["tasks"]
            }}
        )
