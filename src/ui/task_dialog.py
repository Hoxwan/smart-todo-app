import sys
import os
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QComboBox, QDateEdit,
                             QPushButton, QDialogButtonBox)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QKeySequence, QFont
from PyQt5.QtWidgets import QShortcut

# Правильные пути
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from models import Task, Priority, Status

class TaskDialog(QDialog):
    def __init__(self, parent=None, task: Task = None, categories=None):
        super().__init__(parent)
        self.task = task
        self.categories = categories or []
        self.setup_ui()
        self.setup_shortcuts()
        self.load_data()

    def setup_ui(self):
        """Настройка интерфейса диалога"""
        self.setWindowTitle("Добавить задачу" if not self.task else "Редактировать задачу")
        self.setModal(True)
        self.resize(500, 400)

        layout = QVBoxLayout(self)

        # Название задачи
        layout.addWidget(QLabel("Название:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Введите название задачи")
        layout.addWidget(self.title_input)

        # Описание
        layout.addWidget(QLabel("Описание:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("Введите описание задачи")
        layout.addWidget(self.description_input)

        # Приоритет и статус
        priority_status_layout = QHBoxLayout()

        priority_status_layout.addWidget(QLabel("Приоритет:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems([p.value for p in Priority])
        priority_status_layout.addWidget(self.priority_combo)

        priority_status_layout.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems([s.value for s in Status])
        priority_status_layout.addWidget(self.status_combo)

        layout.addLayout(priority_status_layout)

        # Срок выполнения
        layout.addWidget(QLabel("Срок выполнения:"))
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate())
        self.due_date_edit.setMinimumDate(QDate.currentDate())
        layout.addWidget(self.due_date_edit)

        # Категория
        layout.addWidget(QLabel("Категория:"))
        self.category_combo = QComboBox()
        self.load_categories()
        layout.addWidget(self.category_combo)

        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.validate_and_accept)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.reject)

    def load_categories(self):
        """Загрузка категорий в комбобокс"""
        self.category_combo.clear()
        self.category_combo.addItem("Без категории", None)
        for category in self.categories:
            self.category_combo.addItem(category.name, category.id)

    def load_data(self):
        """Загрузка данных задачи"""
        if self.task:
            self.title_input.setText(self.task.title)
            self.description_input.setText(self.task.description)
            self.priority_combo.setCurrentText(self.task.priority.value)
            self.status_combo.setCurrentText(self.task.status.value)
            if self.task.due_date:
                self.due_date_edit.setDate(QDate(
                    self.task.due_date.year,
                    self.task.due_date.month,
                    self.task.due_date.day
                ))

            # Установка категории
            if self.task.category_id:
                for i in range(self.category_combo.count()):
                    if self.category_combo.itemData(i) == self.task.category_id:
                        self.category_combo.setCurrentIndex(i)
                        break

    def validate_and_accept(self):
        """Валидация данных и принятие диалога"""
        if not self.title_input.text().strip():
            self.title_input.setFocus()
            self.title_input.setStyleSheet("border: 1px solid #e74c3c;")
            return

        self.accept()

    def get_task_data(self):
        """Получение данных задачи из формы"""
        return {
            'title': self.title_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'priority': Priority(self.priority_combo.currentText()),
            'status': Status(self.status_combo.currentText()),
            'due_date': self.due_date_edit.date().toPyDate(),
            'category_id': self.category_combo.currentData()
        }