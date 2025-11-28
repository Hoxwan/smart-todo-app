import os
import sys
import logging
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QLabel, QLineEdit,
                             QComboBox, QMessageBox, QShortcut, QListWidgetItem,
                             QMenu, QAction, QInputDialog, QProgressBar, QApplication, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDate, QSettings
from PyQt5.QtGui import QKeySequence, QPixmap, QIcon, QPainter, QColor, QFont
from PyQt5.QtMultimedia import QSound

# Правильные пути для импорта
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from database import DatabaseManager
from models import Task, Category, Priority, Status

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    task_double_clicked = pyqtSignal(Task)

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.current_filter = "all"
        self.current_tasks = []
        self.settings = QSettings("SmartTodo", "TaskManager")
        self.setup_ui()
        self.setup_shortcuts()
        self.load_tasks()
        self.load_categories()

        # Инициализация настроек
        self.apply_settings()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Task Manager")
        self.setGeometry(100, 100, 900, 700)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout
        main_layout = QVBoxLayout(central_widget)

        # Заголовок с кнопкой настроек
        header_layout = QHBoxLayout()
        title_label = QLabel("Task Manager")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.settings_btn = QPushButton("Настройки")
        self.settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(self.settings_btn)

        main_layout.addLayout(header_layout)

        # Панель поиска и фильтрации
        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск задач...")
        self.search_input.textChanged.connect(self.search_tasks)
        filter_layout.addWidget(self.search_input)

        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["Все приоритеты", "Низкий", "Средний", "Высокий"])
        self.priority_filter.currentTextChanged.connect(self.filter_tasks)
        filter_layout.addWidget(self.priority_filter)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все статусы", "В ожидании", "В процессе", "Завершено"])
        self.status_filter.currentTextChanged.connect(self.filter_tasks)
        filter_layout.addWidget(self.status_filter)

        main_layout.addLayout(filter_layout)

        # Статистика
        stats_layout = QHBoxLayout()
        self.total_label = QLabel("Всего задач: 0")
        self.completed_label = QLabel("Завершено: 0")
        self.progress_bar = QProgressBar()

        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.completed_label)
        stats_layout.addWidget(self.progress_bar)
        stats_layout.addStretch()

        main_layout.addLayout(stats_layout)

        # Основной контент
        content_layout = QHBoxLayout()

        # Панель категорий
        category_widget = QWidget()
        category_widget.setMaximumWidth(200)
        category_layout = QVBoxLayout(category_widget)

        category_label = QLabel("Категории")
        category_label.setStyleSheet("font-weight: bold;")
        category_layout.addWidget(category_label)

        self.category_list = QListWidget()
        self.category_list.itemClicked.connect(self.on_category_selected)
        self.category_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.category_list.customContextMenuRequested.connect(self.show_category_context_menu)
        category_layout.addWidget(self.category_list)

        add_category_btn = QPushButton("Добавить категорию")
        add_category_btn.clicked.connect(self.add_category)
        category_layout.addWidget(add_category_btn)

        content_layout.addWidget(category_widget)

        # Список задач
        tasks_widget = QWidget()
        tasks_layout = QVBoxLayout(tasks_widget)

        tasks_label = QLabel("Задачи")
        tasks_label.setStyleSheet("font-weight: bold;")
        tasks_layout.addWidget(tasks_label)

        self.tasks_list = QListWidget()
        self.tasks_list.itemDoubleClicked.connect(self.on_task_double_clicked)
        self.tasks_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tasks_list.customContextMenuRequested.connect(self.show_context_menu)
        tasks_layout.addWidget(self.tasks_list)

        # Кнопки управления задачами
        buttons_layout = QHBoxLayout()

        self.add_btn = QPushButton("Добавить задачу")
        self.add_btn.clicked.connect(self.add_task)
        buttons_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.clicked.connect(self.edit_task)
        buttons_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Удалить задачу")
        self.delete_btn.clicked.connect(self.delete_task)
        buttons_layout.addWidget(self.delete_btn)

        self.complete_btn = QPushButton("Завершить")
        self.complete_btn.clicked.connect(self.complete_task)
        buttons_layout.addWidget(self.complete_btn)

        tasks_layout.addLayout(buttons_layout)

        content_layout.addWidget(tasks_widget)

        main_layout.addLayout(content_layout)

    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.add_task)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.edit_task)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.delete_task)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.focus_search)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.open_settings)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.refresh_tasks)

    def focus_search(self):
        """Фокусировка на поле поиска"""
        self.search_input.setFocus()
        logger.info("Фокус на поле поиска (Ctrl+F)")

    def refresh_tasks(self):
        """Обновление списка задач"""
        self.load_tasks()
        logger.info("Список задач обновлен (F5)")

    def search_tasks(self, text):
        """Поиск задач"""
        try:
            if text.strip():
                tasks = self.db.search_tasks(text.strip())
                self.display_tasks(tasks)
            else:
                self.load_tasks()
        except Exception as e:
            logger.error(f"Ошибка поиска задач: {e}")

    def filter_tasks(self):
        """Фильтрация задач по приоритету и статусу"""
        try:
            priority_filter = self.priority_filter.currentText()
            status_filter = self.status_filter.currentText()

            filtered_tasks = self.current_tasks.copy()

            # Фильтрация по приоритету
            if priority_filter != "Все приоритеты":
                filtered_tasks = [t for t in filtered_tasks if t.priority.value == priority_filter]

            # Фильтрация по статусу
            if status_filter != "Все статусы":
                filtered_tasks = [t for t in filtered_tasks if t.status.value == status_filter]

            self.display_tasks(filtered_tasks)
        except Exception as e:
            logger.error(f"Ошибка фильтрации задач: {e}")

    def load_tasks(self):
        """Загрузка задач из базы данных"""
        try:
            self.tasks_list.clear()
            self.current_tasks = self.db.get_all_tasks()

            for task in self.current_tasks:
                item = QListWidgetItem()

                # Форматирование текста задачи
                status_icon = "✓" if task.status == Status.COMPLETED else "○"
                priority_color = {
                    Priority.LOW: "🟢",
                    Priority.MEDIUM: "🟡",
                    Priority.HIGH: "🔴"
                }

                item_text = f"{status_icon} {task.title} {priority_color[task.priority]}"
                if task.due_date:
                    item_text += f" 📅 {task.due_date.strftime('%d.%m.%Y')}"

                item.setText(item_text)
                item.setData(Qt.UserRole, task)

                # Установка цвета в зависимости от статуса
                if task.status == Status.COMPLETED:
                    item.setBackground(QColor("#d4edda"))
                elif task.priority == Priority.HIGH:
                    item.setBackground(QColor("#f8d7da"))
                elif task.priority == Priority.MEDIUM:
                    item.setBackground(QColor("#fff3cd"))

                self.tasks_list.addItem(item)

            self.update_statistics()
        except Exception as e:
            logger.error(f"Ошибка загрузки задач: {e}")

    def load_categories(self):
        """Загрузка категорий"""
        try:
            self.category_list.clear()

            # Добавление "Все задачи"
            all_item = QListWidgetItem("📁 Все задачи")
            all_item.setData(Qt.UserRole, "all")
            self.category_list.addItem(all_item)

            categories = self.db.get_categories()
            for category in categories:
                item = QListWidgetItem(f"📁 {category.name}")
                item.setData(Qt.UserRole, category.id)
                self.category_list.addItem(item)
        except Exception as e:
            logger.error(f"Ошибка загрузки категорий: {e}")

    def on_category_selected(self, item):
        """Обработка выбора категории"""
        try:
            category_data = item.data(Qt.UserRole)
            if category_data == "all":
                self.current_filter = "all"
                self.load_tasks()
            else:
                self.current_filter = f"category_{category_data}"
                tasks = self.db.get_tasks_by_category(category_data)
                self.display_tasks(tasks)
        except Exception as e:
            logger.error(f"Ошибка выбора категории: {e}")

    def display_tasks(self, tasks):
        """Отображение списка задач"""
        try:
            self.tasks_list.clear()
            self.current_tasks = tasks
            for task in tasks:
                item = QListWidgetItem(task.title)
                item.setData(Qt.UserRole, task)
                self.tasks_list.addItem(item)
        except Exception as e:
            logger.error(f"Ошибка отображения задач: {e}")

    def update_statistics(self):
        """Обновление статистики"""
        try:
            tasks = self.db.get_all_tasks()
            total = len(tasks)
            completed = len([t for t in tasks if t.status == Status.COMPLETED])

            self.total_label.setText(f"Всего задач: {total}")
            self.completed_label.setText(f"Завершено: {completed}")

            progress = int((completed / total) * 100) if total > 0 else 0
            self.progress_bar.setValue(progress)
        except Exception as e:
            logger.error(f"Ошибка обновления статистики: {e}")

    def add_task(self):
        """Добавление новой задачи"""
        try:
            from ui.task_dialog import TaskDialog
            categories = self.db.get_categories()
            dialog = TaskDialog(self, categories=categories)
            if dialog.exec_() == QDialog.Accepted:
                task_data = dialog.get_task_data()
                new_task = Task(
                    id=None,
                    title=task_data['title'],
                    description=task_data['description'],
                    priority=task_data['priority'],
                    status=task_data['status'],
                    due_date=task_data['due_date'],
                    created_at=datetime.now(),
                    category_id=task_data['category_id']
                )
                self.db.add_task(new_task)
                self.load_tasks()
                self.play_notification_sound()
                logger.info("Новая задача добавлена")
        except Exception as e:
            logger.error(f"Ошибка при добавлении задачи: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить задачу: {e}")

    def edit_task(self):
        """Редактирование выбранной задачи"""
        try:
            current_item = self.tasks_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Предупреждение", "Выберите задачу для редактирования")
                return

            task = current_item.data(Qt.UserRole)
            from ui.task_dialog import TaskDialog
            categories = self.db.get_categories()
            dialog = TaskDialog(self, task, categories)
            if dialog.exec_() == QDialog.Accepted:
                updated_data = dialog.get_task_data()
                task.title = updated_data['title']
                task.description = updated_data['description']
                task.priority = updated_data['priority']
                task.status = updated_data['status']
                task.due_date = updated_data['due_date']
                task.category_id = updated_data['category_id']

                self.db.update_task(task)
                self.load_tasks()
                logger.info(f"Задача '{task.title}' обновлена")
        except Exception as e:
            logger.error(f"Ошибка при редактировании задачи: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось редактировать задачу: {e}")

    def delete_task(self):
        """Удаление выбранной задачи"""
        try:
            current_item = self.tasks_list.currentItem()
            if not current_item:
                return

            task = current_item.data(Qt.UserRole)

            # Проверка настройки подтверждения удаления
            confirm_deletion = self.settings.value("confirm_deletion", True, type=bool)
            if confirm_deletion:
                reply = QMessageBox.question(
                    self,
                    "Подтверждение удаления",
                    f"Вы уверены, что хотите удалить задачу '{task.title}'?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return

            self.db.delete_task(task.id)
            self.load_tasks()
            self.play_notification_sound()
            logger.info(f"Задача '{task.title}' удалена")
        except Exception as e:
            logger.error(f"Ошибка при удалении задачи: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить задачу: {e}")

    def complete_task(self):
        """Отметка задачи как выполненной"""
        try:
            current_item = self.tasks_list.currentItem()
            if not current_item:
                return

            task = current_item.data(Qt.UserRole)
            task.status = Status.COMPLETED
            self.db.update_task(task)
            self.load_tasks()
            self.play_notification_sound()
            logger.info(f"Задача '{task.title}' завершена")
        except Exception as e:
            logger.error(f"Ошибка при завершении задачи: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось завершить задачу: {e}")


    def on_task_double_clicked(self, item):
        """Обработка двойного клика по задаче"""
        try:
            task = item.data(Qt.UserRole)
            self.task_double_clicked.emit(task)
            logger.info(f"Двойной клик по задаче: {task.title}")
        except Exception as e:
            logger.error(f"Ошибка при двойном клике по задаче: {e}")

    def show_context_menu(self, position):
        """Показ контекстного меню"""
        try:
            menu = QMenu()

            edit_action = QAction("Редактировать", self)
            edit_action.triggered.connect(self.edit_task)
            menu.addAction(edit_action)

            delete_action = QAction("Удалить", self)
            delete_action.triggered.connect(self.delete_task)
            menu.addAction(delete_action)

            complete_action = QAction("Завершить", self)
            complete_action.triggered.connect(self.complete_task)
            menu.addAction(complete_action)

            menu.exec_(self.tasks_list.mapToGlobal(position))
            logger.info("Открыто контекстное меню")
        except Exception as e:
            logger.error(f"Ошибка при показе контекстного меню: {e}")

    def show_category_context_menu(self, position):
        """Показ контекстного меню для категорий"""
        try:
            item = self.category_list.itemAt(position)
            if not item:
                return

            category_data = item.data(Qt.UserRole)
            if category_data == "all":
                return

            menu = QMenu()
            delete_action = QAction("Удалить категорию", self)
            delete_action.triggered.connect(lambda: self.delete_category(category_data, item.text()))
            menu.addAction(delete_action)
            menu.exec_(self.category_list.mapToGlobal(position))
        except Exception as e:
            logger.error(f"Ошибка при показе контекстного меню категории: {e}")

    def delete_category(self, category_id: int, category_name: str):
        """Удаление категории"""
        try:
            display_name = category_name.replace("📁 ", "")

            reply = QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить категорию '{display_name}'?\n\n"
                f"Все задачи в этой категории будут перемещены в 'Без категории'.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                success = self.db.delete_category(category_id)
                if success:
                    self.load_categories()
                    self.load_tasks()
                    self.play_notification_sound()
                    QMessageBox.information(self, "Успех", f"Категория '{display_name}' удалена")
                    logger.info(f"Категория '{display_name}' удалена")
        except Exception as e:
            logger.error(f"Ошибка при удалении категории: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить категорию: {e}")

    def add_category(self):
        """Добавление новой категории"""
        try:
            name, ok = QInputDialog.getText(self, "Новая категория", "Введите название категории:")
            if ok and name:
                existing_categories = self.db.get_categories()
                if any(cat.name.lower() == name.lower() for cat in existing_categories):
                    QMessageBox.warning(self, "Ошибка", "Категория с таким названием уже существует")
                    return

                new_category = Category(
                    id=None,
                    name=name,
                    color="#3498db",  # Цвет по умолчанию
                    created_at=datetime.now()
                )
                self.db.add_category(new_category)
                self.load_categories()
                self.play_notification_sound()
                logger.info(f"Добавлена категория: {name}")
        except Exception as e:
            logger.error(f"Ошибка при добавлении категории: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить категорию: {e}")

    def open_settings(self):
        """Открытие окна настроек"""
        try:
            from ui.settings_window import SettingsWindow
            settings_window = SettingsWindow(self)
            settings_window.settings_changed.connect(self.on_settings_changed)
            settings_window.exec_()
            logger.info("Открыто окно настроек")
        except Exception as e:
            logger.error(f"Ошибка при открытии настроек: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть настройки: {e}")

    def on_settings_changed(self, settings_dict):
        """Обработчик изменения настроек"""
        try:
            # Сохраняем настройки
            for key, value in settings_dict.items():
                if key == 'font':
                    self.settings.setValue("font_family", value.family())
                    self.settings.setValue("font_size", value.pointSize())
                else:
                    self.settings.setValue(key, value)

            # Применяем настройки немедленно
            self.apply_settings()

        except Exception as e:
            logger.error(f"Ошибка применения измененных настроек: {e}")

    def apply_settings(self):
        """Применение настроек из QSettings"""
        try:
            # Применение темы
            theme = self.settings.value("theme", "Светлая")
            self.apply_theme(theme)

            # Применение шрифта
            font_family = self.settings.value("font_family", "Arial")
            font_size = self.settings.value("font_size", 10, type=int)
            font = QFont(font_family, font_size)
            self.setFont(font)

            logger.info("Настройки применены")

        except Exception as e:
            logger.error(f"Ошибка применения настроек: {e}")

    def apply_theme(self, theme_name):
        """Применение выбранной темы"""
        try:
            if theme_name == "Темная":
                dark_style = """
                QMainWindow, QDialog, QWidget {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QListWidget, QLineEdit, QComboBox, QTextEdit, QDateEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #5a6c7d;
                    border-radius: 4px;
                }
                QLabel {
                    color: #ecf0f1;
                }
                QProgressBar {
                    border: 1px solid #5a6c7d;
                    border-radius: 4px;
                    background-color: #34495e;
                    color: white;
                }
                QProgressBar::chunk {
                    background-color: #27ae60;
                    border-radius: 3px;
                }
                """
                self.setStyleSheet(dark_style)
            else:
                # Светлая тема
                self.setStyleSheet("")
        except Exception as e:
            logger.error(f"Ошибка применения темы: {e}")

    def play_notification_sound(self):
        """Воспроизведение звука уведомления с учетом настроек"""
        try:
            sound_enabled = self.settings.value("sound_enabled", True, type=bool)
            if not sound_enabled:
                return

            # Пытаемся найти звуковой файл в разных местах
            sound_paths = [
                Path(__file__).parent.parent.parent / "resources" / "sounds" / "notification.wav",
                Path("resources/sounds/notification.wav"),
                Path("notification.wav")
            ]

            for sound_path in sound_paths:
                if sound_path.exists():
                    QSound.play(str(sound_path))
                    logger.info("Воспроизведен звук уведомления")
                    return

            logger.warning("Звуковой файл не найден")

        except Exception as e:
            logger.error(f"Ошибка воспроизведения звука: {e}")