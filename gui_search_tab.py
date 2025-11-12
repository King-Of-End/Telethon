from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QSpinBox, QDateEdit, QGroupBox, QFormLayout, QHeaderView)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QFont

from gui import TaskManagerUI


class SearchTab(QWidget):
    def __init__(self, _parent: TaskManagerUI):
        super().__init__()
        self._parent = _parent
        tab = self
        layout = QVBoxLayout(tab)

        title = QLabel("Поиск задач в базе данных")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        search_group = QGroupBox("Условия поиска")
        search_layout = QFormLayout()

        self.search_task_input = QLineEdit()
        self.search_task_input.setPlaceholderText("Ключевые слова для поиска")
        search_layout.addRow("Текст задачи:", self.search_task_input)

        self.search_date_from = QDateEdit()
        self.search_date_from.setCalendarPopup(True)
        self.search_date_from.setSpecialValueText("Не задана")
        search_layout.addRow("Дата от:", self.search_date_from)

        self.search_date_to = QDateEdit()
        self.search_date_to.setCalendarPopup(True)
        self.search_date_to.setDate(QDate.currentDate())
        self.search_date_to.setSpecialValueText("Не задана")
        search_layout.addRow("Дата до:", self.search_date_to)

        self.search_priority_from = QSpinBox()
        self.search_priority_from.setMinimum(0)
        self.search_priority_from.setMaximum(10)
        self.search_priority_from.setSpecialValueText("Любой")
        search_layout.addRow("Приоритет от:", self.search_priority_from)

        self.search_priority_to = QSpinBox()
        self.search_priority_to.setMinimum(0)
        self.search_priority_to.setMaximum(10)
        self.search_priority_to.setValue(10)
        self.search_priority_to.setSpecialValueText("Любой")
        search_layout.addRow("Приоритет до:", self.search_priority_to)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        buttons_layout = QHBoxLayout()

        search_button = QPushButton("Найти")
        search_button.clicked.connect(self.on_search_clicked)
        buttons_layout.addWidget(search_button)

        clear_button = QPushButton("Очистить условия")
        clear_button.clicked.connect(self.on_search_clear_clicked)
        buttons_layout.addWidget(clear_button)

        show_all_button = QPushButton("Показать все")
        show_all_button.clicked.connect(self.on_search_show_all_clicked)
        buttons_layout.addWidget(show_all_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        results_group = QGroupBox("Результаты поиска")
        results_layout = QVBoxLayout()
        self.search_results_label = QLabel("Найдено записей: 0")
        results_layout.addWidget(self.search_results_label)

        self.search_table = QTableWidget()
        self.search_table.setColumnCount(6)
        self.search_table.setHorizontalHeaderLabels(["ID", "Задача", "Дата", "Время", "Приоритет", "Doc ID"])
        self.search_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.search_table.setAlternatingRowColors(True)
        self.search_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.search_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        results_layout.addWidget(self.search_table)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

    def on_search_clicked(self):
        """Обработчик поиска"""
        query = self.search_task_input.text()
        # Здесь будет логика поиска
        self._parent.statusBar().showMessage(f"Поиск: {query}")

    def on_search_clear_clicked(self):
        """Очистка условий поиска"""
        self.search_task_input.clear()
        self.search_date_from.clear()
        self.search_date_to.setDate(QDate.currentDate())
        self.search_priority_from.setValue(0)
        self.search_priority_to.setValue(10)
        self._parent.statusBar().showMessage("Условия поиска очищены")

    def on_search_show_all_clicked(self):
        """Показать все записи"""
        # Здесь будет логика показа всех записей
        self._parent.statusBar().showMessage("Загрузка всех записей...")
