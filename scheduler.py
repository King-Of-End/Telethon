import asyncio
import sqlite3
import threading
import time
from typing import List


def remind():
    print('Пора')


class Scheduler:
    _instance: 'Scheduler | None' = None

    def __new__(cls, *args, **kwargs) -> 'Scheduler':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,
                 database_path: str = 'reminders.db',
                 cycle_time: float = 3600,
                 ) -> None:
        self.database_path: str = database_path
        self.cycle_time: float = cycle_time
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.database_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time REAL NOT NULL,
                    text TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)

    def _save(self, ts: float, text: str) -> None:
        with sqlite3.connect(self.database_path) as con:
            con.execute(
                "INSERT INTO reminders(time, text, status) VALUES (?, ?, 'scheduled')",
                (ts, text)
            )

    def _mark_fired(self, rid: int) -> None:
        with sqlite3.connect(self.database_path) as con:
            con.execute(
                "UPDATE reminders SET status='fired' WHERE id=?",
                (rid,)
            )

    def get_reminders(self) -> List[tuple]:
        with sqlite3.connect(self.database_path) as con:
            res = con.execute(
                "SELECT id, time, text, status FROM reminders"
            ).fetchall()
            return res

    def check_reminders(self):
        reminders: List[tuple] = self.get_reminders()
        for reminder in reminders:
            rid, rtime, text, status = reminder
            current_time: float = time.time()
            remaining_time: float = rtime - current_time
            if remaining_time <= self.cycle_time:
                thread = threading.Thread(target=self._schedule, args=(remaining_time, rid))
                thread.daemon = True
                thread.start()


    def _schedule(self, seconds: float, rid: int) -> None:
        time.sleep(seconds)
        print('Пора')
        self._mark_fired(rid)

    def add_reminder(self, rtime: float, text: str) -> None:
        self._save(rtime, text)
        self.check_reminders()
        print('Добавлено')


Scheduler().add_reminder(time.time() + 10, 'Привет')
