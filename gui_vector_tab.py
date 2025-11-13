from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
                             QTableWidget, QSpinBox, QGroupBox, QFormLayout, QHeaderView, QSplitter, QTableWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from gui import TaskManagerUI, sql_db
import sqlite3
from tools import functions

search_similar = functions['search_similar']


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
        self.vector_query_input.setPlaceholderText(
            "Введите запрос для семантического поиска...\nНапример: 'задачи связанные с работой' или 'срочные дела'")
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
        self.vector_output_text.setReadOnly(True)
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
        self.vector_table.itemSelectionChanged.connect(self.on_row_selected)
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
        threshold = self.vector_threshold_input.value() / 100.0  # Конвертируем в 0-1

        if not query.strip():
            self._parent.statusBar().showMessage("Введите запрос для поиска")
            return

        try:
            self._parent.statusBar().showMessage(f"Выполняется векторный поиск...")

            # Выполняем векторный поиск
            results = search_similar(query, k)

            if not results:
                self.vector_output_text.setPlainText("Результаты не найдены")
                self.vector_table.setRowCount(0)
                self.vector_results_label.setText("Найдено записей: 0")
                self._parent.statusBar().showMessage("Результаты не найдены")
                return

            # Фильтруем по порогу релевантности
            filtered_results = []
            con = sqlite3.connect(sql_db)
            cur = con.cursor()

            for result in results:
                # Получаем score из результата
                score = result.get('score', 0)

                # Проверяем порог
                if True:
                    # Получаем данные задачи из БД по doc_id
                    doc_id = result.get('node', dict()).get('id_', '')

                    if doc_id:
                        request = f'''SELECT id, task, date, time, priority, doc_id FROM active WHERE doc_id="{doc_id}"'''
                        task_data = cur.execute(request).fetchone()

                        if task_data:
                            filtered_results.append({
                                'id': task_data[0],
                                'task': task_data[1],
                                'date': task_data[2],
                                'time': task_data[3],
                                'priority': task_data[4],
                                'doc_id': task_data[5],
                                'score': score,
                                'text': result.get('text', '')
                            })

            con.close()

            # Заполняем таблицу
            self.vector_table.setRowCount(len(filtered_results))

            for row_idx, result in enumerate(filtered_results):
                self.vector_table.setItem(row_idx, 0, QTableWidgetItem(str(result['id'])))
                self.vector_table.setItem(row_idx, 1, QTableWidgetItem(result['task']))
                self.vector_table.setItem(row_idx, 2, QTableWidgetItem(result['date']))
                self.vector_table.setItem(row_idx, 3, QTableWidgetItem(result['time']))
                self.vector_table.setItem(row_idx, 4, QTableWidgetItem(str(result['priority'])))
                self.vector_table.setItem(row_idx, 5, QTableWidgetItem(result['doc_id']))
                self.vector_table.setItem(row_idx, 6, QTableWidgetItem(f"{result['score']:.2%}"))

            self.vector_table.resizeColumnsToContents()
            self.vector_results_label.setText(f"Найдено записей: {len(filtered_results)}")

            # Формируем детальную информацию
            detail_text = f"Запрос: {query}\n"
            detail_text += f"Найдено результатов: {len(filtered_results)}\n"
            detail_text += f"Порог релевантности: {threshold:.0%}\n\n"
            detail_text += "=" * 50 + "\n\n"

            for i, result in enumerate(filtered_results, 1):
                detail_text += f"Результат #{i}:\n"
                detail_text += f"ID: {result['id']}\n"
                detail_text += f"Задача: {result['task']}\n"
                detail_text += f"Дата: {result['date']}, Время: {result['time']}\n"
                detail_text += f"Приоритет: {result['priority']}\n"
                detail_text += f"Релевантность: {result['score']:.2%}\n"
                detail_text += "-" * 50 + "\n\n"

            self.vector_output_text.setPlainText(detail_text)

            self._parent.statusBar().showMessage(f"Найдено {len(filtered_results)} результатов")

        except Exception as e:
            error_text = f"Ошибка при векторном поиске: {str(e)}"
            self.vector_output_text.setPlainText(error_text)
            self._parent.statusBar().showMessage(f"Ошибка: {str(e)}")

    def on_row_selected(self):
        """Обработчик выбора строки в таблице"""
        selected_rows = self.vector_table.selectionModel().selectedRows()

        if selected_rows:
            row = selected_rows[0].row()

            # Получаем данные из выбранной строки
            task_id = self.vector_table.item(row, 0).text()
            task = self.vector_table.item(row, 1).text()
            date = self.vector_table.item(row, 2).text()
            time = self.vector_table.item(row, 3).text()
            priority = self.vector_table.item(row, 4).text()
            doc_id = self.vector_table.item(row, 5).text()
            score = self.vector_table.item(row, 6).text()

            # Обновляем детальную информацию
            detail_text = f"Выбранная задача:\n\n"
            detail_text += f"ID: {task_id}\n"
            detail_text += f"Задача: {task}\n"
            detail_text += f"Дата: {date}\n"
            detail_text += f"Время: {time}\n"
            detail_text += f"Приоритет: {priority}\n"
            detail_text += f"Doc ID: {doc_id}\n"
            detail_text += f"Релевантность: {score}\n"

            # Сохраняем предыдущий текст и добавляем информацию о выборе
            current_text = self.vector_output_text.toPlainText()
            if "Выбранная задача:" not in current_text:
                self.vector_output_text.setPlainText(current_text + "\n\n" + "=" * 50 + "\n\n" + detail_text)

    def on_vector_clear_clicked(self):
        """Очистка результатов векторного поиска"""
        self.vector_query_input.clear()
        self.vector_output_text.clear()
        self.vector_table.setRowCount(0)
        self.vector_results_label.setText("Найдено записей: 0")
        self._parent.statusBar().showMessage("Результаты очищены")