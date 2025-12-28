import os.path

from tools import create_clear_db
from telegram import start_telegram_app
from scheduler import Scheduler

def main():
    if not os.path.exists('databases/sqlite/tasks.sqlite'):
        create_clear_db()
    scheduler = Scheduler()
    scheduler.start()
    print('scheduler started')
    start_telegram_app()
    print('telegram started')


if __name__ == '__main__':
    main()
