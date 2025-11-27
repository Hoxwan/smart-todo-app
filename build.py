# build.py
import PyInstaller.__main__
import os
import shutil
from pathlib import Path


def build_app():
    BASE_DIR = Path(__file__).parent
    SRC_DIR = BASE_DIR / "src"
    RESOURCES_DIR = BASE_DIR / "resources"
    FORMS_DIR = BASE_DIR / "forms"

    # Очистка предыдущих сборок
    if (BASE_DIR / "build").exists():
        shutil.rmtree(BASE_DIR / "build")
    if (BASE_DIR / "dist").exists():
        shutil.rmtree(BASE_DIR / "dist")

    # Аргументы для PyInstaller
    args = [
        str(SRC_DIR / "main.py"),
        '--name=SmartTodoApp',
        '--windowed',  # Без консоли
        '--onedir',  # Папка с exe (рекомендуется для разработки)
        # '--onefile',  # Один exe файл (для распространения)
        f'--add-data={RESOURCES_DIR}{os.pathsep}resources',
        f'--add-data={FORMS_DIR}{os.pathsep}forms',
        '--add-data=tasks.db;.',  # Для Windows
        '--add-data=requirements.txt;.',
        # Скрытые импорты
        '--hidden-import=ui.main_window',
        '--hidden-import=ui.settings_window',
        '--hidden-import=ui.task_dialog',
        '--hidden-import=database',
        '--hidden-import=models',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=PySide6.QtSql',
        '--hidden-import=PySide6.QtMultimedia',
        # Иконка
        '--icon=resources/images/icon.ico' if (RESOURCES_DIR / "images" / "icon.ico").exists() else '',
        '--clean',
        '--noconfirm'
    ]

    # Убираем пустые аргументы
    args = [arg for arg in args if arg]

    print("Сборка Smart Todo App...")
    print(f"Аргументы: {args}")

    PyInstaller.__main__.run(args)

    print("\nСборка завершена!")
    print("EXE файл находится в папке 'dist/SmartTodoApp/'")


if __name__ == "__main__":
    build_app()