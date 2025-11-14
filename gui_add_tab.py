from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,QLabel, QLineEdit, QPushButton, QTableWidget, QSpinBox,
                             QDateEdit, QTimeEdit, QGroupBox, QFormLayout, QHeaderView)
from PyQt6.QtCore import QDate, QTime
from PyQt6.QtGui import QFont

from gui import TaskManagerUI, draw_to_table

from tools import functions

add_task = functions['add_task']
search_tasks_database = functions['search_tasks_database']
update_task = functions['update_task']
delete_task = functions['delete_task']
search_similar = functions['search_similar']


class AddTab(QWidget):
    def __init__(self, _parent: TaskManagerUI):
        super().__init__()
        self._parent = _parent
        tab = self
        layout = QVBoxLayout(tab)

        title = QLabel("Добавление новой задачи")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        form_group = QGroupBox("Параметры задачи")
        form_layout = QFormLayout()

        self.add_task_input = QLineEdit()
        self.add_task_input.setPlaceholderText("Описание задачи")
        form_layout.addRow("Задача:", self.add_task_input)

        self.add_date_input = QDateEdit()
        self.add_date_input.setCalendarPopup(True)
        self.add_date_input.setDate(QDate.currentDate())
        self.add_date_input.setSpecialValueText("Не указана")
        self.add_date_input.setMinimumDate(QDate(2000, 1, 1))
        form_layout.addRow("Дата:", self.add_date_input)

        self.add_time_input = QTimeEdit()
        self.add_time_input.setTime(QTime.currentTime())
        self.add_time_input.setSpecialValueText("Не указано")
        form_layout.addRow("Время:", self.add_time_input)

        self.add_priority_input = QSpinBox()
        self.add_priority_input.setMinimum(1)
        self.add_priority_input.setMaximum(10)
        self.add_priority_input.setValue(5)
        form_layout.addRow("Приоритет (1-10):", self.add_priority_input)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        buttons_layout = QHBoxLayout()

        add_button = QPushButton("Добавить задачу")
        add_button.clicked.connect(self.on_add_task_clicked)
        buttons_layout.addWidget(add_button)

        clear_button = QPushButton("Очистить поля")
        clear_button.clicked.connect(self.on_add_clear_clicked)
        buttons_layout.addWidget(clear_button)

        refresh_button = QPushButton("Обновить таблицу")
        refresh_button.clicked.connect(self.on_add_refresh_clicked)
        buttons_layout.addWidget(refresh_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        table_group = QGroupBox("Существующие задачи")
        table_layout = QVBoxLayout()

        self.add_table = QTableWidget()
        self.add_table.setColumnCount(6)
        self.add_table.setHorizontalHeaderLabels(["ID", "Задача", "Дата", "Время", "Приоритет"])
        self.add_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.add_table.setAlternatingRowColors(True)
        self.add_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.add_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table_layout.addWidget(self.add_table)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        self.update()

    def update(self):
        req = '''SELECT id, task, date, time, priority FROM active'''
        draw_to_table(req, self.add_table)

    def on_add_task_clicked(self):
        task = self.add_task_input.text()
        date = str(self.add_date_input.date().toPyDate())
        raw_time = self.add_time_input.time().toPyTime()
        time = str(':'.join([str(raw_time.hour), str(raw_time.minute)]))
        priority = self.add_priority_input.value()
        self._parent.statusBar().showMessage(f"Добавление задачи: {task}")
        res = add_task(task, date, time, priority)
        self._parent.statusBar().showMessage(res)

    def on_add_clear_clicked(self):
        """Очистка полей добавления"""
        self.add_task_input.clear()
        self.add_date_input.setDate(QDate.currentDate())
        self.add_time_input.setTime(QTime.currentTime())
        self.add_priority_input.setValue(5)
        self._parent.statusBar().showMessage("Поля очищены")

    def on_add_refresh_clicked(self):
        """Обновление таблицы"""
        req = '''SELECT id, task, date, time, priority FROM active'''
        self.update()
        self._parent.statusBar().showMessage("Обновление таблицы...")
