from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QSpinBox, QGroupBox, QFormLayout, QHeaderView, QMessageBox)
from PyQt6.QtGui import QFont

from gui import TaskManagerUI


class DeleteTab(QWidget):
    def __init__(self, _parent: TaskManagerUI):
        super().__init__()
        tab = self
        self._parent = _parent
        layout = QVBoxLayout(tab)

        title = QLabel("Удаление задач")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        delete_group = QGroupBox("Условие удаления")
        delete_layout = QFormLayout()

        self.delete_id_input = QSpinBox()
        self.delete_id_input.setMinimum(0)
        self.delete_id_input.setMaximum(999999)
        self.delete_id_input.setSpecialValueText("Не задан")
        delete_layout.addRow("ID задачи:", self.delete_id_input)

        self.delete_search_input = QLineEdit()
        self.delete_search_input.setPlaceholderText("Текст для поиска задачи")
        delete_layout.addRow("ИЛИ текст задачи:", self.delete_search_input)

        self.delete_priority_input = QSpinBox()
        self.delete_priority_input.setMinimum(0)
        self.delete_priority_input.setMaximum(10)
        self.delete_priority_input.setSpecialValueText("Не задан")
        delete_layout.addRow("ИЛИ приоритет:", self.delete_priority_input)

        delete_group.setLayout(delete_layout)
        layout.addWidget(delete_group)

        buttons_layout = QHBoxLayout()

        delete_button = QPushButton("Удалить задачу")
        delete_button.clicked.connect(self.on_delete_task_clicked)
        buttons_layout.addWidget(delete_button)

        clear_button = QPushButton("Очистить условия")
        clear_button.clicked.connect(self.on_delete_clear_clicked)
        buttons_layout.addWidget(clear_button)

        refresh_button = QPushButton("Обновить таблицу")
        refresh_button.clicked.connect(self.on_delete_refresh_clicked)
        buttons_layout.addWidget(refresh_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        deleted_group = QGroupBox("Удаленные задачи")
        deleted_layout = QVBoxLayout()

        self.delete_count_label = QLabel("Удалено записей: 0")
        deleted_layout.addWidget(self.delete_count_label)

        self.delete_table = QTableWidget()
        self.delete_table.setColumnCount(6)
        self.delete_table.setHorizontalHeaderLabels(["ID", "Задача", "Дата", "Время", "Приоритет", "Doc ID"])
        self.delete_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.delete_table.setAlternatingRowColors(True)
        self.delete_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.delete_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        deleted_layout.addWidget(self.delete_table)

        restore_button = QPushButton("Восстановить выбранную задачу")
        restore_button.clicked.connect(self.on_restore_task_clicked)
        deleted_layout.addWidget(restore_button)

        deleted_group.setLayout(deleted_layout)
        layout.addWidget(deleted_group)

    def on_delete_task_clicked(self):
        """Обработчик удаления задачи"""
        task_id = self.delete_id_input.value()
        # Здесь будет логика удаления
        self._parent.statusBar().showMessage(f"Удаление задачи с ID: {task_id}")

    def on_delete_clear_clicked(self):
        """Очистка условий удаления"""
        self.delete_id_input.setValue(0)
        self.delete_search_input.clear()
        self.delete_priority_input.setValue(0)
        self._parent.statusBar().showMessage("Условия удаления очищены")

    def on_delete_refresh_clicked(self):
        """Обновление таблицы удаленных"""
        # Здесь будет логика обновления
        self._parent.statusBar().showMessage("Обновление таблицы удаленных...")

    def on_restore_task_clicked(self):
        """Восстановление выбранной задачи"""
        selected_rows = self.delete_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            # Здесь будет логика восстановления
            self._parent.statusBar().showMessage(f"Восстановление задачи из строки {row}")
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите задачу для восстановления")
