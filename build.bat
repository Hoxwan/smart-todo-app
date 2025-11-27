@echo off
echo Установка PyInstaller...
pip install pyinstaller

echo Сборка Smart Todo App...
python build_simple.py

echo.
echo ========================================
echo Сборка завершена!
echo EXE файл: dist\SmartTodoApp\SmartTodoApp.exe
echo ========================================
pause