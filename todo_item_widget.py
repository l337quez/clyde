from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QLineEdit, QProgressBar
)
from PySide6.QtCore import Qt


class EditableLine(QLineEdit):
    def __init__(self, text):
        super().__init__(text)
        self.setReadOnly(True)
        self.setFixedHeight(36)

    def mouseDoubleClickEvent(self, event):
        self.setReadOnly(False)
        self.setFocus()

    def focusOutEvent(self, event):
        self.setReadOnly(True)
        super().focusOutEvent(event)


class TodoItemWidget(QWidget):
    def __init__(self, title, description, tasks, on_delete, on_update):
        super().__init__()
        self.setObjectName("TodoItem")

        self.title = title
        self.description = description
        self.tasks = tasks
        self.on_delete = on_delete
        self.on_update = on_update
        self.checkboxes = []

        self.layout = QVBoxLayout(self)

        self.setStyleSheet("""
            QWidget#TodoItem {
                background-color: #fdfdfd;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 10px;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #d00;
            }
        """)

        header_layout = QHBoxLayout()
        self.toggle_button = QPushButton("🔽")
        self.toggle_button.setFixedSize(36, 36)
        self.toggle_button.clicked.connect(self.toggle_subtasks)
        header_layout.addWidget(self.toggle_button)

        self.main_checkbox = QCheckBox()
        self.main_checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
            }
        """)
        self.main_checkbox.stateChanged.connect(self.on_main_checkbox_change)
        header_layout.addWidget(self.main_checkbox)

        self.title_label = QLabel(f"<b>{self.title}</b>")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        self.delete_button = QPushButton("🗑")
        self.delete_button.setFixedSize(36, 36)
        self.delete_button.clicked.connect(lambda: self.on_delete(self))
        header_layout.addWidget(self.delete_button)

        self.layout.addLayout(header_layout)

        self.subtask_container = QWidget()
        self.subtask_layout = QVBoxLayout(self.subtask_container)
        self.subtask_container.setVisible(True)
        self.layout.addWidget(self.subtask_container)

        if self.description:
            desc = QLabel(self.description)
            desc.setWordWrap(True)
            self.subtask_layout.addWidget(desc)

        self.tasks_layout = QVBoxLayout()
        self.subtask_layout.addLayout(self.tasks_layout)

        self.progress_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setTextVisible(False)
        self.subtask_layout.addWidget(self.progress_label)
        self.subtask_layout.addWidget(self.progress_bar)

        for task in self.tasks:
            self.add_subtask(task.get("task", ""), task.get("checked", False))

        self.add_subtask_btn = QPushButton("+ Add Subtask")
        self.add_subtask_btn.clicked.connect(self.add_subtask_prompt)
        self.subtask_layout.addWidget(self.add_subtask_btn)

        self.update_progress()

    def toggle_subtasks(self):
        is_visible = self.subtask_container.isVisible()
        self.subtask_container.setVisible(not is_visible)
        self.toggle_button.setText("▶️" if is_visible else "🔽")

    def add_subtask_prompt(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        input_field = QLineEdit()
        input_field.setPlaceholderText("New subtask")
        input_field.setMinimumHeight(36)
        input_field.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 6px 10px;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #3b99fc;
            }
        """)

        confirm_btn = QPushButton("✔")
        confirm_btn.setFixedSize(36, 36)
        confirm_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                background-color: #dff0d8;
                border: 1px solid #c1e2b3;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c8e5bc;
            }
        """)

        container = QWidget()
        container.setLayout(layout)

        layout.addWidget(input_field)
        layout.addWidget(confirm_btn)

        self.tasks_layout.addWidget(container)
        self.tasks_layout.addSpacing(6)
        input_field.setFocus()

        def confirm():
            text = input_field.text().strip()
            if text:
                self.tasks_layout.removeWidget(container)
                container.deleteLater()
                self.add_subtask(text, False)
                self.save_changes()

        input_field.returnPressed.connect(confirm)
        confirm_btn.clicked.connect(confirm)

    def add_subtask(self, text, checked=False):
        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
            }
            QCheckBox {
                margin: 4px;
            }
        """)
        checkbox.stateChanged.connect(self.save_changes)

        text_input = EditableLine(text)
        text_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                background-color: #fff;
                border-radius: 8px;
                font-size: 14px;
                padding: 6px 10px;
            }
            QLineEdit:focus {
                border: 1px solid #3b99fc;
            }
        """)
        text_input.editingFinished.connect(self.save_changes)

        delete_btn = QPushButton("❌")
        delete_btn.setFixedSize(36, 36)
        delete_btn.setStyleSheet("QPushButton { font-size: 16px; }")

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignVCenter)

        layout.addWidget(checkbox)
        layout.addWidget(text_input, 1)
        layout.addWidget(delete_btn)

        delete_btn.clicked.connect(lambda: self.remove_subtask(container))

        self.tasks_layout.addWidget(container)
        self.tasks_layout.addSpacing(6)
        self.checkboxes.append((container, checkbox, text_input))
        self.update_progress()

    def remove_subtask(self, container):
        for i, (cont, _, _) in enumerate(self.checkboxes):
            if cont == container:
                self.checkboxes.pop(i)
                break
        self.tasks_layout.removeWidget(container)
        container.deleteLater()
        self.save_changes()

    def on_main_checkbox_change(self, state):
        checked = state == Qt.Checked
        for _, checkbox, _ in self.checkboxes:
            checkbox.blockSignals(True)
            checkbox.setChecked(checked)
            checkbox.blockSignals(False)
        self.save_changes()

    def update_progress(self):
        total = len(self.checkboxes)
        done = 0
        for _, checkbox, text_input in self.checkboxes:
            if checkbox.isChecked():
                done += 1
                text_input.setStyleSheet("""
                    QLineEdit {
                        text-decoration: line-through;
                        color: gray;
                        border: 1px solid #ccc;
                        border-radius: 8px;
                        font-size: 14px;
                        padding: 6px 10px;
                        background: #fafafa;
                    }
                """)
            else:
                text_input.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid #ccc;
                        background-color: #fff;
                        border-radius: 8px;
                        font-size: 14px;
                        padding: 6px 10px;
                    }
                    QLineEdit:focus {
                        border: 1px solid #3b99fc;
                    }
                """)

        self.progress_label.setText(f"{done}/{total} subtasks completed")
        self.progress_bar.setValue(int((done / total) * 100) if total > 0 else 0)

        if total > 0:
            if done == total:
                self.main_checkbox.setCheckState(Qt.Checked)
            elif done == 0:
                self.main_checkbox.setCheckState(Qt.Unchecked)
            else:
                self.main_checkbox.setTristate(True)
                self.main_checkbox.setCheckState(Qt.PartiallyChecked)

    def save_changes(self):
        updated_tasks = []
        for _, checkbox, text_input in self.checkboxes:
            updated_tasks.append({
                "task": text_input.text(),
                "checked": checkbox.isChecked()
            })
        self.tasks = updated_tasks
        self.update_progress()
        self.on_update(self)

    def get_data(self):
        return {
            "title": self.title,
            "description": self.description,
            "tasks": self.tasks
        }

    def get_title(self):
        return self.title
