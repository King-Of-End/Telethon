import os.path
from tools import create_clear_db
from gui import start_gui

def main():
    if not os.path.exists('databases/sqlite/tasks.sqlite'):
        create_clear_db()
    start_gui()

if __name__ == '__main__':
    main()
