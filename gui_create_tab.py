from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox,
                             QDateEdit, QTimeEdit, QGroupBox, QFormLayout)
from PyQt6.QtCore import QDate, QTime
from PyQt6.QtGui import QFont

from gui import TaskManagerUI, draw_to_table, sql_db
import sqlite3
from tools import functions

update_task = functions['update_task']
search_tasks_database = functions['search_tasks_database']


class CreateTab(QWidget):

    def __init__(self, _parent: TaskManagerUI):
        super().__init__()
        self._parent = _parent
        self.current_task_id = None  # Хранение ID найденной задачи
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
        self.update_info_text.setReadOnly(True)
        info_layout.addWidget(self.update_info_text)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()

    def on_update_find_clicked(self):
        """Поиск задачи для обновления"""
        task_id = self.update_id_input.value()
        search_text = self.update_search_input.text()

        try:
            con = sqlite3.connect(sql_db)
            cur = con.cursor()

            if search_text:
                # Поиск по тексту задачи
                request = f'''SELECT id, task, date, time, priority, doc_id FROM active WHERE task LIKE "%{search_text}%"'''
                results = cur.execute(request).fetchall()

                if results:
                    # Берем первый результат
                    task_data = results[0]
                    self.current_task_id = task_data[0]

                    info_text = f"""ID: {task_data[0]}
Задача: {task_data[1]}
Дата: {task_data[2]}
Время: {task_data[3]}
Приоритет: {task_data[4]}
Doc ID: {task_data[5]}

Найдено задач: {len(results)}"""

                    self.update_info_text.setPlainText(info_text)

                    # Заполняем поля текущими значениями
                    self.update_new_task.setText(task_data[1])
                    if task_data[2]:
                        date_parts = task_data[2].split('-')
                        self.update_new_date.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
                    if task_data[3]:
                        time_parts = task_data[3].split(':')
                        self.update_new_time.setTime(QTime(int(time_parts[0]), int(time_parts[1])))
                    self.update_new_priority.setValue(int(task_data[4]))

                    self._parent.statusBar().showMessage(f"Найдено задач: {len(results)}, показана первая")
                else:
                    self.update_info_text.setPlainText("Задачи не найдены")
                    self._parent.statusBar().showMessage("Задачи не найдены")
            else:
                # Поиск по ID
                request = f'''SELECT id, task, date, time, priority, doc_id FROM active WHERE id={task_id}'''
                result = cur.execute(request).fetchone()

                if result:
                    self.current_task_id = result[0]

                    info_text = f"""ID: {result[0]}
Задача: {result[1]}
Дата: {result[2]}
Время: {result[3]}
Приоритет: {result[4]}
Doc ID: {result[5]}"""

                    self.update_info_text.setPlainText(info_text)

                    # Заполняем поля текущими значениями
                    self.update_new_task.setText(result[1])
                    if result[2]:
                        date_parts = result[2].split('-')
                        self.update_new_date.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
                    if result[3]:
                        time_parts = result[3].split(':')
                        self.update_new_time.setTime(QTime(int(time_parts[0]), int(time_parts[1])))
                    self.update_new_priority.setValue(int(result[4]))

                    self._parent.statusBar().showMessage(f"Задача найдена: ID {task_id}")
                else:
                    self.update_info_text.setPlainText(f"Задача с ID {task_id} не найдена")
                    self._parent.statusBar().showMessage(f"Задача с ID {task_id} не найдена")

            con.close()
        except Exception as e:
            self.update_info_text.setPlainText(f"Ошибка при поиске: {str(e)}")
            self._parent.statusBar().showMessage(f"Ошибка: {str(e)}")

    def on_update_task_clicked(self):
        """Обработчик обновления задачи"""
        if self.current_task_id is None:
            self._parent.statusBar().showMessage("Сначала найдите задачу для обновления")
            return

        # Собираем новые значения
        new_task = self.update_new_task.text() if self.update_new_task.text() else None
        new_date = str(
            self.update_new_date.date().toPyDate()) if self.update_new_date.date() != QDate.currentDate() else None
        raw_time = self.update_new_time.time().toPyTime()
        new_time = str(':'.join(
            [str(raw_time.hour), str(raw_time.minute)])) if self.update_new_time.time() != QTime.currentTime() else None
        new_priority = self.update_new_priority.value() if self.update_new_priority.value() != 0 else None

        # Вызываем функцию обновления
        result = update_task(
            task_id=self.current_task_id,
            task=new_task,
            date=new_date,
            time=new_time,
            priority=new_priority
        )

        self._parent.statusBar().showMessage(f"Обновление задачи: {result}")

        if result == "Успешно":
            # Обновляем информацию
            self.on_update_find_clicked()

    def on_update_clear_clicked(self):
        """Очистка полей обновления"""
        self.update_id_input.setValue(1)
        self.update_search_input.clear()
        self.update_new_task.clear()
        self.update_new_date.setDate(QDate.currentDate())
        self.update_new_time.setTime(QTime.currentTime())
        self.update_new_priority.setValue(0)
        self.update_info_text.clear()
        self.current_task_id = None
        self._parent.statusBar().showMessage("Поля очищены")