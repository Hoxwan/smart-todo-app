import sqlite3
import logging
from datetime import datetime
from typing import List, Optional
from models import Task, Category, Priority, Status

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Таблица категорий
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        color TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Таблица задач
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT,
                        priority TEXT NOT NULL,
                        status TEXT NOT NULL,
                        due_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        category_id INTEGER,
                        FOREIGN KEY (category_id) REFERENCES categories (id)
                    )
                ''')

                # Создание начальных категорий
                default_categories = [
                    ("Работа", "#FF6B6B"),
                    ("Личное", "#4ECDC4"),
                    ("Учеба", "#45B7D1"),
                    ("Покупки", "#96CEB4")
                ]

                cursor.executemany(
                    "INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)",
                    default_categories
                )

                conn.commit()
                logger.info("Database initialized successfully")

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def add_task(self, task: Task) -> int:
        """Добавление новой задачи"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tasks (title, description, priority, status, due_date, category_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    task.title,
                    task.description,
                    task.priority.value,
                    task.status.value,
                    task.due_date.isoformat() if task.due_date else None,
                    task.category_id
                ))
                task_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Task added with ID: {task_id}")
                return task_id
        except sqlite3.Error as e:
            logger.error(f"Error adding task: {e}")
            raise

    def get_all_tasks(self) -> List[Task]:
        """Получение всех задач"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.id, t.title, t.description, t.priority, t.status, 
                           t.due_date, t.created_at, t.category_id
                    FROM tasks t
                    ORDER BY t.created_at DESC
                ''')
                tasks = []
                for row in cursor.fetchall():
                    try:
                        task = Task(
                            id=row[0],
                            title=row[1],
                            description=row[2],
                            priority=Priority(row[3]),
                            status=Status(row[4]),
                            due_date=datetime.fromisoformat(row[5]) if row[5] else None,
                            created_at=datetime.fromisoformat(row[6]),
                            category_id=row[7]
                        )
                        tasks.append(task)
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Skipping invalid task data: {e}")
                        continue
                return tasks
        except sqlite3.Error as e:
            logger.error(f"Error getting tasks: {e}")
            return []

    def update_task(self, task: Task) -> bool:
        """Обновление задачи"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tasks 
                    SET title=?, description=?, priority=?, status=?, due_date=?, category_id=?
                    WHERE id=?
                ''', (
                    task.title,
                    task.description,
                    task.priority.value,
                    task.status.value,
                    task.due_date.isoformat() if task.due_date else None,
                    task.category_id,
                    task.id
                ))
                conn.commit()
                success = cursor.rowcount > 0
                if success:
                    logger.info(f"Task {task.id} updated")
                return success
        except sqlite3.Error as e:
            logger.error(f"Error updating task: {e}")
            return False

    def delete_task(self, task_id: int) -> bool:
        """Удаление задачи"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM tasks WHERE id=?', (task_id,))
                conn.commit()
                success = cursor.rowcount > 0
                if success:
                    logger.info(f"Task {task_id} deleted")
                return success
        except sqlite3.Error as e:
            logger.error(f"Error deleting task: {e}")
            return False

    def get_categories(self) -> List[Category]:
        """Получение всех категорий"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, name, color, created_at FROM categories')
                categories = []
                for row in cursor.fetchall():
                    category = Category(
                        id=row[0],
                        name=row[1],
                        color=row[2],
                        created_at=datetime.fromisoformat(row[3])
                    )
                    categories.append(category)
                return categories
        except sqlite3.Error as e:
            logger.error(f"Error getting categories: {e}")
            return []

    def add_category(self, category: Category) -> int:
        """Добавление новой категории"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO categories (name, color) VALUES (?, ?)',
                    (category.name, category.color)
                )
                category_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Category added with ID: {category_id}")
                return category_id
        except sqlite3.Error as e:
            logger.error(f"Error adding category: {e}")
            raise

    def delete_category(self, category_id: int) -> bool:
        """Удаление категории"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Сначала обновляем задачи этой категории (устанавливаем category_id = NULL)
                cursor.execute('UPDATE tasks SET category_id = NULL WHERE category_id = ?', (category_id,))

                # Затем удаляем категорию
                cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))

                conn.commit()
                success = cursor.rowcount > 0
                if success:
                    logger.info(f"Category {category_id} deleted")
                return success
        except sqlite3.Error as e:
            logger.error(f"Error deleting category: {e}")
            return False
    def get_tasks_by_category(self, category_id: int) -> List[Task]:
        """Получение задач по категории"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, description, priority, status, due_date, created_at, category_id
                    FROM tasks 
                    WHERE category_id=?
                    ORDER BY created_at DESC
                ''', (category_id,))

                tasks = []
                for row in cursor.fetchall():
                    task = Task(
                        id=row[0],
                        title=row[1],
                        description=row[2],
                        priority=Priority(row[3]),
                        status=Status(row[4]),
                        due_date=datetime.fromisoformat(row[5]) if row[5] else None,
                        created_at=datetime.fromisoformat(row[6]),
                        category_id=row[7]
                    )
                    tasks.append(task)
                return tasks
        except sqlite3.Error as e:
            logger.error(f"Error getting tasks by category: {e}")
            return []

    def search_tasks(self, search_text: str) -> List[Task]:
        """Поиск задач по тексту"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, description, priority, status, due_date, created_at, category_id
                    FROM tasks 
                    WHERE title LIKE ? OR description LIKE ?
                    ORDER BY created_at DESC
                ''', (f'%{search_text}%', f'%{search_text}%'))

                tasks = []
                for row in cursor.fetchall():
                    task = Task(
                        id=row[0],
                        title=row[1],
                        description=row[2],
                        priority=Priority(row[3]),
                        status=Status(row[4]),
                        due_date=datetime.fromisoformat(row[5]) if row[5] else None,
                        created_at=datetime.fromisoformat(row[6]),
                        category_id=row[7]
                    )
                    tasks.append(task)
                return tasks
        except sqlite3.Error as e:
            logger.error(f"Error searching tasks: {e}")
            return []
