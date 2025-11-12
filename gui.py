import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout,QTabWidget

class TaskManagerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Менеджер задач с ИИ")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        from gui_ai_tab import AiTab
        from gui_add_tab import AddTab
        from gui_search_tab import SearchTab
        from gui_create_tab import CreateTab
        from gui_delete_tab import DeleteTab
        from gui_vector_tab import VectorSearchTab

        self.tabs.addTab(AiTab(self), "Взаимодействие с ИИ")
        self.tabs.addTab(AddTab(self), "Добавить в БД")
        self.tabs.addTab(SearchTab(self), "Искать по БД")
        self.tabs.addTab(CreateTab(self), "Обновить в БД")
        self.tabs.addTab(DeleteTab(self), "Удалить из БД")
        self.tabs.addTab(VectorSearchTab(self), "Векторный поиск")

        self.statusBar().showMessage("Готов к работе")

def start_gui():
    """Точка входа в приложение"""
    app = QApplication(sys.argv)

    # Установка стиля приложения
    app.setStyle('Fusion')

    # Создание и отображение главного окна
    window = TaskManagerUI()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    start_gui()
