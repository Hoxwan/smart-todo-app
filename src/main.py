import sys
import os
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QPixmap, QFont

# Определяем базовый путь для ресурсов
if getattr(sys, 'frozen', False):
    # Если приложение собрано в exe
    BASE_DIR = Path(sys.executable).parent
else:
    # При разработке
    BASE_DIR = Path(__file__).parent.parent

# Добавляем пути для импорта
sys.path.insert(0, str(BASE_DIR / "src"))

# Устанавливаем пути для ресурсов
RESOURCES_PATH = BASE_DIR / "resources"
FORMS_PATH = BASE_DIR / "forms"

print(f"BASE_DIR: {BASE_DIR}")
print(f"RESOURCES_PATH: {RESOURCES_PATH}")
print(f"FORMS_PATH: {FORMS_PATH}")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('task_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Глобальный обработчик исключений"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Необработанное исключение:", exc_info=(exc_type, exc_value, exc_traceback))

    QMessageBox.critical(None, "Критическая ошибка",
                         f"Произошла критическая ошибка:\n{str(exc_value)}\n\n"
                         f"Подробности в файле task_manager.log")


sys.excepthook = handle_exception


def apply_application_settings(app):
    """Применение настроек приложения"""
    settings = QSettings("SmartTodo", "TaskManager")

    # Установка шрифта
    font_family = settings.value("font_family", "Arial")
    font_size = settings.value("font_size", 10, type=int)
    app.setFont(QFont(font_family, font_size))

    # Установка стиля
    theme = settings.value("theme", "Светлая")
    if theme == "Темная":
        app.setStyleSheet("""
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
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)


def main():
    """Основная функция приложения"""
    try:
        # Создание приложения
        app = QApplication(sys.argv)
        app.setApplicationName("Умный список задач")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("SmartTodo")

        # Применение настроек
        apply_application_settings(app)

        # Загрузка splash screen
        splash = None
        try:
            splash_path = Path(__file__).parent.parent / "resources" / "images" / "splash.png"
            if splash_path.exists():
                splash_pixmap = QPixmap(str(splash_path))
                splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
                splash.show()

                # Отображение сообщения на splash screen
                #splash.showMessage("Загрузка приложения...",
                                   #Qt.AlignBottom | Qt.AlignCenter,
                                   #Qt.white)
        except Exception as e:
            logger.warning(f"Не удалось загрузить splash screen: {e}")

        # Импортируем после создания QApplication
        from ui.main_window import MainWindow

        # Создание главного окна
        main_window = MainWindow()

        # Настройка запуска свернутым
        settings = QSettings("SmartTodo", "TaskManager")
        start_minimized = settings.value("start_minimized", False, type=bool)

        # Закрытие splash screen и отображение главного окна
        def show_main_window():
            if splash:
                splash.close()
            if not start_minimized:
                main_window.show()
            else:
                main_window.showMinimized()
            logger.info("Приложение успешно запущено")

        # Имитация загрузки
        QTimer.singleShot(2000, show_main_window)

        # Запуск приложения
        return_code = app.exec_()
        logger.info("Приложение завершено")
        return return_code

    except Exception as e:
        logger.critical(f"Ошибка запуска приложения: {e}")
        QMessageBox.critical(None, "Ошибка запуска",
                             f"Не удалось запустить приложение:\n{str(e)}")
        return 1


def show_category_context_menu(self, position):
    """Показ контекстного меню для категорий"""
    item = self.category_list.itemAt(position)
    if not item:
        return

    category_data = item.data(Qt.UserRole)

    # Не показываем меню для "Все задачи"
    if category_data == "all":
        return

    menu = QMenu()

    delete_action = QAction("Удалить категорию", self)
    delete_action.triggered.connect(lambda: self.delete_category(category_data, item.text()))
    menu.addAction(delete_action)

    menu.exec_(self.category_list.mapToGlobal(position))
    logger.info("Открыто контекстное меню для категории")

if __name__ == "__main__":
    sys.exit(main())