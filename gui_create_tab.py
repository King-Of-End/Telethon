from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox,
                             QDateEdit, QTimeEdit, QGroupBox, QFormLayout)
from PyQt6.QtCore import QDate, QTime
from PyQt6.QtGui import QFont

from gui import TaskManagerUI


class CreateTab(QWidget):

    def __init__(self, _parent: TaskManagerUI):
        super().__init__()
        self._parent = _parent
        tab = self
        layout = QVBoxLayout(tab)

        title = QLabel("Обновление задачи")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        search_group = QGroupBox("Условие поиска задачи")
        search_layout = QFormLayout()

        self.update_id_input = QSpinBox()
        self.update_id_input.setMinimum(1)
        self.update_id_input.setMaximum(999999)
        search_layout.addRow("ID задачи:", self.update_id_input)

        self.update_search_input = QLineEdit()
        self.update_search_input.setPlaceholderText("Текст для поиска задачи")
        search_layout.addRow("ИЛИ текст задачи:", self.update_search_input)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        find_button = QPushButton("Найти задачу")
        find_button.setMaximumWidth(200)
        find_button.clicked.connect(self.on_update_find_clicked)
        layout.addWidget(find_button)

        update_group = QGroupBox("Новые значения")
        update_layout = QFormLayout()

        self.update_new_task = QLineEdit()
        self.update_new_task.setPlaceholderText("Новое описание задачи")
        update_layout.addRow("Новая задача:", self.update_new_task)

        self.update_new_date = QDateEdit()
        self.update_new_date.setCalendarPopup(True)
        self.update_new_date.setDate(QDate.currentDate())
        self.update_new_date.setSpecialValueText("Не изменять")
        update_layout.addRow("Новая дата:", self.update_new_date)

        self.update_new_time = QTimeEdit()
        self.update_new_time.setTime(QTime.currentTime())
        self.update_new_time.setSpecialValueText("Не изменять")
        update_layout.addRow("Новое время:", self.update_new_time)

        self.update_new_priority = QSpinBox()
        self.update_new_priority.setMinimum(0)
        self.update_new_priority.setMaximum(10)
        self.update_new_priority.setSpecialValueText("Не изменять")
        update_layout.addRow("Новый приоритет:", self.update_new_priority)

        update_group.setLayout(update_layout)
        layout.addWidget(update_group)

        buttons_layout = QHBoxLayout()

        update_button = QPushButton("Обновить задачу")
        update_button.clicked.connect(self.on_update_task_clicked)
        buttons_layout.addWidget(update_button)

        clear_button = QPushButton("Очистить поля")
        clear_button.clicked.connect(self.on_update_clear_clicked)
        buttons_layout.addWidget(clear_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        info_group = QGroupBox("Информация о текущей задаче")
        info_layout = QVBoxLayout()

        self.update_info_text = QTextEdit()
        self.update_info_text.setMaximumHeight(150)
        self.update_info_text.setPlaceholderText("Найдите задачу для отображения информации")
        info_layout.addWidget(self.update_info_text)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()


    def on_update_find_clicked(self):
        """Поиск задачи для обновления"""
        task_id = self.update_id_input.value()
        # Здесь будет логика поиска
        self._parent.statusBar().showMessage(f"Поиск задачи с ID: {task_id}")

    def on_update_task_clicked(self):
        """Обработчик обновления задачи"""
        # Здесь будет логика обновления
        self._parent.statusBar().showMessage("Обновление задачи...")

    def on_update_clear_clicked(self):
        """Очистка полей обновления"""
        self.update_id_input.setValue(1)
        self.update_search_input.clear()
        self.update_new_task.clear()
        self.update_new_date.setDate(QDate.currentDate())
        self.update_new_time.setTime(QTime.currentTime())
        self.update_new_priority.setValue(0)
        self.update_info_text.clear()
        self._parent.statusBar().showMessage("Поля очищены")
