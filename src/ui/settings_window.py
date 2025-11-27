import sys
import os
import logging
from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QCheckBox, QSlider,
                             QGroupBox, QColorDialog, QFontDialog, QMessageBox,
                             QTabWidget, QWidget, QSpinBox, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QSettings
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtMultimedia import QSound

# Добавляем путь к модулям
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

logger = logging.getLogger(__name__)


class SettingsWindow(QDialog):
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("SmartTodo", "TaskManager")
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Настройка интерфейса настроек"""
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.resize(500, 600)

        layout = QVBoxLayout(self)

        # Вкладки
        self.tab_widget = QTabWidget()

        # Вкладка общего вида
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)

        # Настройки темы
        theme_group = QGroupBox("Внешний вид")
        theme_layout = QFormLayout(theme_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Темная", "Системная"])
        theme_layout.addRow("Тема:", self.theme_combo)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["Русский", "Английский"])
        theme_layout.addRow("Язык:", self.language_combo)

        general_layout.addWidget(theme_group)

        # Настройки поведения
        behavior_group = QGroupBox("Поведение")
        behavior_layout = QVBoxLayout(behavior_group)

        self.auto_save_check = QCheckBox("Автосохранение при изменении")
        behavior_layout.addWidget(self.auto_save_check)

        self.start_minimized_check = QCheckBox("Запуск свернутым")
        behavior_layout.addWidget(self.start_minimized_check)

        self.confirm_deletion_check = QCheckBox("Подтверждение при удалении")
        self.confirm_deletion_check.setChecked(True)
        behavior_layout.addWidget(self.confirm_deletion_check)

        general_layout.addWidget(behavior_group)

        # Настройки шрифта
        font_group = QGroupBox("Шрифт")
        font_layout = QVBoxLayout(font_group)

        self.font_button = QPushButton("Выбрать шрифт")
        self.font_button.clicked.connect(self.select_font)
        font_layout.addWidget(self.font_button)

        self.font_label = QLabel("Текущий шрифт: Arial, 10pt")
        font_layout.addWidget(self.font_label)

        general_layout.addWidget(font_group)
        general_layout.addStretch()

        # Вкладка уведомлений
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout(notifications_tab)

        # Настройки звука
        sound_group = QGroupBox("Звуковые уведомления")
        sound_layout = QVBoxLayout(sound_group)

        self.sound_check = QCheckBox("Включить звуковые уведомления")
        sound_layout.addWidget(self.sound_check)

        sound_layout.addWidget(QLabel("Громкость:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.test_sound)
        sound_layout.addWidget(self.volume_slider)

        self.test_sound_btn = QPushButton("Тестовый звук")
        self.test_sound_btn.clicked.connect(self.test_sound)
        sound_layout.addWidget(self.test_sound_btn)

        notifications_layout.addWidget(sound_group)

        # Настройки всплывающих уведомлений
        popup_group = QGroupBox("Всплывающие уведомления")
        popup_layout = QVBoxLayout(popup_group)

        self.desktop_notifications_check = QCheckBox("Показывать уведомления на рабочем столе")
        popup_layout.addWidget(self.desktop_notifications_check)

        self.notification_timeout_spin = QSpinBox()
        self.notification_timeout_spin.setRange(1, 60)
        self.notification_timeout_spin.setValue(5)
        self.notification_timeout_spin.setSuffix(" секунд")

        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Время показа:"))
        timeout_layout.addWidget(self.notification_timeout_spin)
        timeout_layout.addStretch()
        popup_layout.addLayout(timeout_layout)

        notifications_layout.addWidget(popup_group)
        notifications_layout.addStretch()

        # Добавление вкладок
        self.tab_widget.addTab(general_tab, "Общие")
        self.tab_widget.addTab(notifications_tab, "Уведомления")

        layout.addWidget(self.tab_widget)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.apply_btn = QPushButton("Применить")
        self.apply_btn.clicked.connect(self.apply_settings)
        buttons_layout.addWidget(self.apply_btn)

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_btn)

        self.reset_btn = QPushButton("Сброс")
        self.reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.reset_btn)

        layout.addLayout(buttons_layout)

        # Применение стилей
        self.apply_styles()

    def apply_styles(self):
        """Применение CSS стилей"""
        style = """
        QDialog {
            background-color: #f8f9fa;
        }
        QGroupBox {
            font-weight: bold;
            margin-top: 10px;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            padding: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #2c3e50;
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
        QTabWidget::pane {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
        }
        QTabBar::tab {
            background-color: #ecf0f1;
            padding: 8px 16px;
            margin-right: 2px;
            border-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #3498db;
            color: white;
        }
        """
        self.setStyleSheet(style)

    def load_settings(self):
        """Загрузка сохраненных настроек"""
        try:
            # Настройки темы
            theme = self.settings.value("theme", "Светлая")
            index = self.theme_combo.findText(theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)

            # Настройки поведения
            self.auto_save_check.setChecked(
                self.settings.value("auto_save", False, type=bool)
            )
            self.start_minimized_check.setChecked(
                self.settings.value("start_minimized", False, type=bool)
            )
            self.confirm_deletion_check.setChecked(
                self.settings.value("confirm_deletion", True, type=bool)
            )

            # Настройки уведомлений
            self.sound_check.setChecked(
                self.settings.value("sound_enabled", True, type=bool)
            )
            self.volume_slider.setValue(
                self.settings.value("volume", 50, type=int)
            )
            self.desktop_notifications_check.setChecked(
                self.settings.value("desktop_notifications", True, type=bool)
            )
            self.notification_timeout_spin.setValue(
                self.settings.value("notification_timeout", 5, type=int)
            )

            # Настройки шрифта
            font_family = self.settings.value("font_family", "Arial")
            font_size = self.settings.value("font_size", 10, type=int)
            self.current_font = QFont(font_family, font_size)
            self.font_label.setText(f"Текущий шрифт: {font_family}, {font_size}pt")

        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")

    def select_font(self):
        """Выбор шрифта"""
        font, ok = QFontDialog.getFont(self.current_font, self)
        if ok:
            self.current_font = font
            self.font_label.setText(f"Текущий шрифт: {font.family()}, {font.pointSize()}pt")

    def test_sound(self):
        """Тестовое воспроизведение звука"""
        try:
            sound_path = Path(__file__).parent.parent.parent / "resources" / "sounds" / "notification.wav"
            if sound_path.exists():
                sound = QSound(str(sound_path))
                sound.play()
                logger.info("Тестовый звук воспроизведен")
            else:
                QMessageBox.warning(self, "Предупреждение", "Звуковой файл не найден")
        except Exception as e:
            logger.error(f"Ошибка воспроизведения тестового звука: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось воспроизвести звук: {e}")

    def apply_settings(self):
        """Применение настроек"""
        try:
            # Сохранение настроек
            self.settings.setValue("theme", self.theme_combo.currentText())
            self.settings.setValue("language", self.language_combo.currentText())
            self.settings.setValue("auto_save", self.auto_save_check.isChecked())
            self.settings.setValue("start_minimized", self.start_minimized_check.isChecked())
            self.settings.setValue("confirm_deletion", self.confirm_deletion_check.isChecked())
            self.settings.setValue("sound_enabled", self.sound_check.isChecked())
            self.settings.setValue("volume", self.volume_slider.value())
            self.settings.setValue("desktop_notifications", self.desktop_notifications_check.isChecked())
            self.settings.setValue("notification_timeout", self.notification_timeout_spin.value())

            if hasattr(self, 'current_font'):
                self.settings.setValue("font_family", self.current_font.family())
                self.settings.setValue("font_size", self.current_font.pointSize())

            # Отправка сигнала с настройками
            settings_dict = {
                'theme': self.theme_combo.currentText(),
                'language': self.language_combo.currentText(),
                'auto_save': self.auto_save_check.isChecked(),
                'start_minimized': self.start_minimized_check.isChecked(),
                'confirm_deletion': self.confirm_deletion_check.isChecked(),
                'sound_enabled': self.sound_check.isChecked(),
                'volume': self.volume_slider.value(),
                'desktop_notifications': self.desktop_notifications_check.isChecked(),
                'notification_timeout': self.notification_timeout_spin.value(),
                'font': getattr(self, 'current_font', QFont('Arial', 10))
            }

            self.settings_changed.emit(settings_dict)
            QMessageBox.information(self, "Успех", "Настройки применены успешно!")
            logger.info("Настройки применены")

        except Exception as e:
            logger.error(f"Ошибка применения настроек: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось применить настройки: {e}")

    def reset_settings(self):
        """Сброс настроек к значениям по умолчанию"""
        reply = QMessageBox.question(
            self,
            "Сброс настроек",
            "Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.settings.clear()
            self.load_settings()
            QMessageBox.information(self, "Успех", "Настройки сброшены к значениям по умолчанию")
            logger.info("Настройки сброшены")

    def accept(self):
        """Обработка нажатия OK"""
        self.apply_settings()
        super().accept()