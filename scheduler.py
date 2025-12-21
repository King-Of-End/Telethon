import asyncio
import sqlite3
import threading
import time
from typing import List


def remind():
    print('Пора')


class Scheduler:
    _instance: 'Scheduler | None' = None
    _initialised: bool = False

    def __new__(cls, *args, **kwargs) -> 'Scheduler':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,
                 database_path: str = 'reminders.db',
                 cycle_time: float = 3600,
                 ) -> None:
        if self._initialised:
            return
        self.database_path: str = database_path
        self.cycle_time: float = cycle_time
        self._init_db()
        self._initialised = True

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
            con.execute("""
            UPDATE reminders SET status='scheduled' WHERE status='planned'
            """)

    def _add(self, ts: float, text: str) -> None:
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

    def _mark_planned(self, rid: int) -> None:
        with sqlite3.connect(self.database_path) as con:
            con.execute(
                "UPDATE reminders SET status='planned' WHERE id=?",
                (rid,)
            )

    def _get_reminder(self, rid: int) -> str:
        with sqlite3.connect(self.database_path) as con:
            text = con.execute(
                "SELECT text FROM reminders WHERE id=?",
                (rid,)
            ).fetchone()[0]
            return text

    def _get_reminders(self) -> List[tuple]:
        with sqlite3.connect(self.database_path) as con:
            res = con.execute(
                "SELECT id, time, text, status FROM reminders WHERE status='scheduled' ",
            ).fetchall()
            return res

    def start(self) -> None:
        self.check_reminders()
        threading.Thread(
            target=self._main_cycle,
            daemon=True
        ).start()

    def _main_cycle(self):
        while True:
            time.sleep(self.cycle_time)
            self.check_reminders()


    def check_reminders(self):
        reminders: List[tuple] = self._get_reminders()
        for reminder in reminders:
            rid, rtime, text, status = reminder
            current_time: float = time.time()
            remaining_time: float = rtime - current_time
            if remaining_time <= self.cycle_time:
                self._mark_planned(rid)
                threading.Thread(
                    target=self._schedule,
                    daemon=True,
                    args=(remaining_time, rid)
                ).start()

    def _schedule(self, seconds: float, rid: int) -> None:
        time.sleep(seconds)
        print(self._get_reminder(rid), seconds, rid)
        self._mark_fired(rid)


    def add_reminder(self, rtime: float, text: str) -> None:
        self._add(rtime, text)
        self.check_reminders()


async def main() -> None:
    Scheduler().add_reminder(time.time() + 10, 'Привет')
    Scheduler().add_reminder(time.time() + 5, 'Пока')

if __name__ == '__main__':
    asyncio.run(main())