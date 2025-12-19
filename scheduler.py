import asyncio
import sqlite3
from typing import List


class Scheduler:
    _instance: 'Scheduler | None' = None

    def __new__(cls, *args, **kwargs) -> 'Scheduler':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,
                 database_path: str,
                 cycle_time: float = 3600,
                 ) -> None:
        self.database_path: str = database_path
        self.cycle_time: float = cycle_time
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.database_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id TEXT PRIMARY KEY,
                    ts REAL NOT NULL,
                    text TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)

    def _save(self, rid: str, ts: float, text: str) -> None:
        with sqlite3.connect(self.database_path) as con:
            con.execute(
                "INSERT INTO reminders VALUES (?, ?, ?, 'scheduled')",
                (rid, ts, text)
            )

    def _mark_fired(self, rid: str) -> None:
        with sqlite3.connect(self.database_path) as con:
            con.execute(
                "UPDATE reminders SET status='fired' WHERE id=?",
                (rid,)
            )

    def get_reminders(self) -> List[dict]:
        with sqlite3.connect(self.database_path) as con:
            res = con.execute(
                "SELECT id, ts, text, status FROM reminders"
            ).fetchall()
            return res


    def main_cycle(self):
        asyncio.sleep(self.cycle_time)
        self.check_reminders()

    def check_reminders(self):
        pass