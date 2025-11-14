from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QSpinBox, QGroupBox, QFormLayout, QHeaderView, QMessageBox, QTableWidgetItem)
from PyQt6.QtGui import QFont

from gui import TaskManagerUI, draw_to_table, sql_db
import sqlite3
from tools import functions

delete_task = functions['delete_task']


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
        self.on_delete_refresh_clicked()

    def on_delete_task_clicked(self):
        """Обработчик удаления задачи"""
        task_id = self.delete_id_input.value()
        search_text = self.delete_search_input.text()
        priority = self.delete_priority_input.value()

        try:
            con = sqlite3.connect(sql_db)
            cur = con.cursor()

            if task_id > 0:
                check_request = f'''SELECT id FROM active WHERE id={task_id}'''
                result = cur.execute(check_request).fetchone()

                if result:
                    res = delete_task(task_id)
                    self._parent.statusBar().showMessage(f"Удаление задачи ID {task_id}: {res}")

                    if res == "Успешно":
                        self.on_delete_refresh_clicked()
                else:
                    self._parent.statusBar().showMessage(f"Задача с ID {task_id} не найдена")
                    QMessageBox.warning(self, "Предупреждение", f"Задача с ID {task_id} не существует")

            elif search_text:
                find_request = f'''SELECT id FROM active WHERE task LIKE "%{search_text}%"'''
                results = cur.execute(find_request).fetchall()

                if results:
                    reply = QMessageBox.question(
                        self,
                        'Подтверждение удаления',
                        f'Найдено задач: {len(results)}. Удалить все?',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )

                    if reply == QMessageBox.StandardButton.Yes:
                        success_count = 0
                        for row in results:
                            res = delete_task(row[0])
                            if res == "Успешно":
                                success_count += 1

                        self._parent.statusBar().showMessage(f"Удалено задач: {success_count} из {len(results)}")
                        self.on_delete_refresh_clicked()
                else:
                    self._parent.statusBar().showMessage("Задачи не найдены")
                    QMessageBox.information(self, "Информация", "Задачи с таким текстом не найдены")

            elif priority > 0:
                find_request = f'''SELECT id FROM active WHERE priority={priority}'''
                results = cur.execute(find_request).fetchall()

                if results:
                    reply = QMessageBox.question(
                        self,
                        'Подтверждение удаления',
                        f'Найдено задач с приоритетом {priority}: {len(results)}. Удалить все?',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )

                    if reply == QMessageBox.StandardButton.Yes:
                        success_count = 0
                        for row in results:
                            res = delete_task(row[0])
                            if res == "Успешно":
                                success_count += 1

                        self._parent.statusBar().showMessage(f"Удалено задач: {success_count} из {len(results)}")
                        self.on_delete_refresh_clicked()
                else:
                    self._parent.statusBar().showMessage("Задачи не найдены")
                    QMessageBox.information(self, "Информация", f"Задачи с приоритетом {priority} не найдены")
            else:
                QMessageBox.warning(self, "Предупреждение", "Укажите хотя бы один критерий для удаления")

            con.close()

        except Exception as e:
            self._parent.statusBar().showMessage(f"Ошибка при удалении: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def on_delete_clear_clicked(self):
        """Очистка условий удаления"""
        self.delete_id_input.setValue(0)
        self.delete_search_input.clear()
        self.delete_priority_input.setValue(0)
        self._parent.statusBar().showMessage("Условия удаления очищены")

    def on_delete_refresh_clicked(self):
        """Обновление таблицы удаленных"""
        try:
            con = sqlite3.connect(sql_db)
            cur = con.cursor()

            request = '''SELECT id, task, date, time, priority, doc_id FROM deleted'''
            results = cur.execute(request).fetchall()

            self.delete_table.setRowCount(len(results))

            for row_idx, row_data in enumerate(results):
                for col_idx, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    self.delete_table.setItem(row_idx, col_idx, item)

            self.delete_table.resizeColumnsToContents()
            self.delete_count_label.setText(f"Удалено записей: {len(results)}")

            self._parent.statusBar().showMessage(f"Загружено удаленных задач: {len(results)}")
            con.close()

        except Exception as e:
            self._parent.statusBar().showMessage(f"Ошибка при загрузке: {str(e)}")

    def on_restore_task_clicked(self):
        """Восстановление выбранной задачи"""
        selected_rows = self.delete_table.selectionModel().selectedRows()

        if selected_rows:
            row = selected_rows[0].row()

            task_id = int(self.delete_table.item(row, 0).text())
            task = self.delete_table.item(row, 1).text()
            date = self.delete_table.item(row, 2).text()
            time = self.delete_table.item(row, 3).text()
            priority = int(self.delete_table.item(row, 4).text())
            doc_id = self.delete_table.item(row, 5).text()

            try:
                con = sqlite3.connect(sql_db)
                cur = con.cursor()

                restore_request = f'''INSERT INTO active(task, date, time, priority, doc_id) 
                                     VALUES("{task}", "{date}", "{time}", {priority}, "{doc_id}")'''
                cur.execute(restore_request)

                delete_request = f'''DELETE FROM deleted WHERE id={task_id}'''
                cur.execute(delete_request)

                con.commit()
                con.close()

                self._parent.statusBar().showMessage(f"Задача ID {task_id} восстановлена")
                self.on_delete_refresh_clicked()

            except Exception as e:
                self._parent.statusBar().showMessage(f"Ошибка при восстановлении: {str(e)}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось восстановить задачу: {str(e)}")
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите задачу для восстановления")