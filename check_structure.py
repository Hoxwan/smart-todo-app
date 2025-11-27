# check_structure.py
import os
from pathlib import Path


def check_project_structure():
    base_dir = Path(__file__).parent
    print("Структура проекта:")

    for root, dirs, files in os.walk(base_dir):
        level = root.replace(str(base_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")


if __name__ == "__main__":
    check_project_structure()