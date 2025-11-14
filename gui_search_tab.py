from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QSpinBox, QDateEdit, QGroupBox, QFormLayout, QHeaderView)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QFont

from gui import TaskManagerUI, draw_to_table
from tools import functions

add_task = functions['add_task']
search_tasks_database = functions['search_tasks_database']
update_task = functions['update_task']
delete_task = functions['delete_task']
search_similar = functions['search_similar']

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

        self.search_priority_from = QSpinBox()
        self.search_priority_from.setMinimum(0)
        self.search_priority_from.setMaximum(10)
        search_layout.addRow("Приоритет от:", self.search_priority_from)

        self.search_priority_to = QSpinBox()
        self.search_priority_to.setMinimum(0)
        self.search_priority_to.setMaximum(10)
        self.search_priority_to.setValue(10)
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
        self._parent.statusBar().showMessage(f"Поиск")
        task = self.search_task_input.text()
        priority_from = self.search_priority_from.value()
        priority_to = self.search_priority_to.value()
        res = search_tasks_database(task, None, None, [priority_from, priority_to, '>'])
        if res == 'Неуспешно':
            self._parent.statusBar().showMessage('Неуспешно')
        r = draw_to_table('', self.search_table, res)
        if not r:
            self._parent.statusBar().showMessage(f"Успешно")
            return
        self._parent.statusBar().showMessage(r)


    def on_search_clear_clicked(self):
        """Очистка условий поиска"""
        self.search_task_input.clear()
        self.search_priority_from.setValue(0)
        self.search_priority_to.setValue(10)
        self._parent.statusBar().showMessage("Условия поиска очищены")

    def on_search_show_all_clicked(self):
        """Показать все записи"""
        req = '''SELECT id, task, date, time, priority FROM active'''
        draw_to_table(req, self.search_table)
        self._parent.statusBar().showMessage("Загрузка всех записей...")
