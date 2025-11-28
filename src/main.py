import sys
import os
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

# Настройка путей для сборки
if getattr(sys, 'frozen', False):
    # Если приложение собрано в exe
    BASE_DIR = Path(sys.executable).parent
else:
    # При разработке
    BASE_DIR = Path(__file__).parent

# Добавляем пути для импорта
sys.path.insert(0, str(BASE_DIR))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(BASE_DIR / 'task_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Основная функция приложения"""
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        from PyQt5.QtCore import QTimer, QSettings
        from ui.main_window import MainWindow

        # Создание приложения
        app = QApplication(sys.argv)
        app.setApplicationName("Task Manager")
        app.setApplicationVersion("0.12.3")
        app.setOrganizationName("Task Industries")

        # Установка иконки приложения
        icon_path = Path(__file__).parent.parent / "resources" / "images" / "splash.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))

        # Создание главного окна
        main_window = MainWindow()

        # Настройка запуска свернутым
        settings = QSettings("SmartTodo", "TaskManager")
        start_minimized = settings.value("start_minimized", False, type=bool)

        if not start_minimized:
            main_window.show()
        else:
            main_window.showMinimized()

        logger.info("Приложение успешно запущено")

        # Запуск приложения
        return app.exec_()

    except Exception as e:
        logger.critical(f"Ошибка запуска приложения: {e}")
        QMessageBox.critical(None, "Ошибка запуска",
                             f"Не удалось запустить приложение:\n{str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())