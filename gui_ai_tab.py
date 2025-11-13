from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QComboBox, QGroupBox
from PyQt6.QtGui import QFont
from gui import TaskManagerUI

from Graph import app
from states import MessageState


class AiTab(QWidget):
    def __init__(self, parent_: 'TaskManagerUI'):
        super().__init__()
        self.parent_ = parent_
        tab = self
        layout = QVBoxLayout(tab)

        title = QLabel("Взаимодействие с ИИ-ассистентом")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        mode_group = QGroupBox("Режим работы ИИ")
        mode_layout = QHBoxLayout()

        mode_label = QLabel("Выберите режим:")
        mode_layout.addWidget(mode_label)

        self.ai_mode_combo = QComboBox()
        self.ai_mode_combo.addItems(["Локальный", "Онлайн", "Смешанный"])
        self.ai_mode_combo.setMinimumWidth(200)
        mode_layout.addWidget(self.ai_mode_combo)

        mode_layout.addStretch()
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        input_group = QGroupBox("Ввод запроса")
        input_layout = QVBoxLayout()

        self.ai_input_text = QTextEdit()
        self.ai_input_text.setPlaceholderText("Введите ваш запрос к ИИ...")
        self.ai_input_text.setMaximumHeight(150)
        input_layout.addWidget(self.ai_input_text)

        send_button = QPushButton("Отправить запрос")
        send_button.setMaximumWidth(200)
        send_button.clicked.connect(self.on_ai_send_clicked)
        input_layout.addWidget(send_button)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        output_group = QGroupBox("Ответ ИИ")
        output_layout = QVBoxLayout()

        self.ai_output_text = QTextEdit()
        self.ai_output_text.setPlaceholderText("Здесь будет отображен ответ ИИ...")
        output_layout.addWidget(self.ai_output_text)

        clear_button = QPushButton("Очистить историю")
        clear_button.setMaximumWidth(200)
        clear_button.clicked.connect(self.on_ai_clear_clicked)
        output_layout.addWidget(clear_button)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

    def on_ai_send_clicked(self):
        query = self.ai_input_text.toPlainText()
        mode = self.ai_mode_combo.currentText()
        try:
            res = app.invoke(MessageState(user_message=query))['message']
        except Exception:
            res = 'ИИ выдал ошибку'
        self.ai_output_text.setPlainText(res)
        self.parent_.statusBar().showMessage(f"Отправка запроса в режиме: {mode}")

    def on_ai_clear_clicked(self):
        self.ai_input_text.clear()
        self.ai_output_text.clear()
        self.parent_.statusBar().showMessage("История очищена")
