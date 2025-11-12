from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
                             QTableWidget, QSpinBox, QGroupBox, QFormLayout, QHeaderView, QSplitter)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from gui import TaskManagerUI


class VectorSearchTab(QWidget):
    def __init__(self, _parent: TaskManagerUI):
        super().__init__()
        tab = self
        self._parent = _parent
        layout = QVBoxLayout(tab)

        title = QLabel("Векторный поиск")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        search_group = QGroupBox("Параметры векторного поиска")
        search_layout = QFormLayout()

        self.vector_query_input = QTextEdit()
        self.vector_query_input.setPlaceholderText("Введите запрос для семантического поиска...")
        self.vector_query_input.setMaximumHeight(100)
        search_layout.addRow("Запрос:", self.vector_query_input)

        self.vector_k_input = QSpinBox()
        self.vector_k_input.setMinimum(1)
        self.vector_k_input.setMaximum(100)
        self.vector_k_input.setValue(10)
        search_layout.addRow("Количество результатов (k):", self.vector_k_input)

        self.vector_threshold_input = QSpinBox()
        self.vector_threshold_input.setMinimum(0)
        self.vector_threshold_input.setMaximum(100)
        self.vector_threshold_input.setValue(70)
        self.vector_threshold_input.setSuffix("%")
        search_layout.addRow("Порог релевантности:", self.vector_threshold_input)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        buttons_layout = QHBoxLayout()

        search_button = QPushButton("Выполнить векторный поиск")
        search_button.clicked.connect(self.on_vector_search_clicked)
        buttons_layout.addWidget(search_button)

        clear_button = QPushButton("Очистить результаты")
        clear_button.clicked.connect(self.on_vector_clear_clicked)
        buttons_layout.addWidget(clear_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        splitter = QSplitter(Qt.Orientation.Vertical)

        output_group = QGroupBox("Детальная информация")
        output_layout = QVBoxLayout()

        self.vector_output_text = QTextEdit()
        self.vector_output_text.setPlaceholderText("Здесь будет отображена детальная информация о результатах...")
        output_layout.addWidget(self.vector_output_text)

        output_group.setLayout(output_layout)
        splitter.addWidget(output_group)

        results_group = QGroupBox("Результаты поиска")
        results_layout = QVBoxLayout()

        self.vector_results_label = QLabel("Найдено записей: 0")
        results_layout.addWidget(self.vector_results_label)

        self.vector_table = QTableWidget()
        self.vector_table.setColumnCount(7)
        self.vector_table.setHorizontalHeaderLabels(
            ["ID", "Задача", "Дата", "Время", "Приоритет", "Doc ID", "Релевантность"]
        )
        self.vector_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.vector_table.setAlternatingRowColors(True)
        self.vector_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.vector_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        results_layout.addWidget(self.vector_table)

        results_group.setLayout(results_layout)
        splitter.addWidget(results_group)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

    def on_vector_search_clicked(self):
        """Обработчик векторного поиска"""
        query = self.vector_query_input.toPlainText()
        k = self.vector_k_input.value()
        # Здесь будет логика векторного поиска
        self._parent.statusBar().showMessage(f"Векторный поиск: {query} (k={k})")

    def on_vector_clear_clicked(self):
        """Очистка результатов векторного поиска"""
        self.vector_query_input.clear()
        self.vector_output_text.clear()
        self.vector_table.setRowCount(0)
        self.vector_results_label.setText("Найдено записей: 0")
        self._parent.statusBar().showMessage("Результаты очищены")
