import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List
import heapq


def remind():
    print('Пора')


class Scheduler:
    _instance: 'Scheduler | None' = None
    _initialised: bool = False
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> 'Scheduler':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,
                 database_path: str = 'reminders.db',
                 ) -> None:
        if self._initialised:
            return
        self.database_path: str = database_path
        self._init_db()
        self._initialised = True
        self._cycle_thread: threading.Thread | None = None
        self._queue: list[tuple[float, int]] = []
        self._queue_event = threading.Event()
        self._stop_event = threading.Event()
        self._executor = ThreadPoolExecutor(max_workers=10)
        self.start()

    def _init_db(self) -> None:
        """Инициализация базы данных
        Структура базы данных: id | time (абсолютное) | text (исходный) | status
        Варианты status:
        scheduled - изначально при добавлении
        planned - выполнение уже запланировано в _worker
        executing - во время выполнения
        fired - выполнено
        """
        with self._get_connection() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time REAL NOT NULL,
                    text TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)
            con.execute("""
            UPDATE reminders SET status='scheduled' WHERE status in ('planned', 'executing')
            """)

    def _get_connection(self):
        con = sqlite3.connect(self.database_path, timeout=10.0)
        try:
            con.execute("PRAGMA journal_mode=WAL;")
            con.execute("PRAGMA busy_timeout=5000;")
        except Exception:
            pass
        return con

    def _add_to_database(self, ts: float, text: str) -> int:
        with self._get_connection() as con:
            cur = con.execute(
                "INSERT INTO reminders(time, text, status) VALUES (?, ?, 'scheduled')",
                (ts, text)
            )
            return cur.lastrowid

    def _mark_planned_in_database(self, rid: int) -> None:
        with self._get_connection() as con:
            con.execute(
                "UPDATE reminders SET status='planned' WHERE id=?",
                (rid,)
            )

    def _mark_executing_in_database(self, rid: int) -> None:
        with self._get_connection() as con:
            con.execute(
                "UPDATE reminders SET status='executing' WHERE id=?",
                (rid,)
            )

    def _mark_fired_in_database(self, rid: int) -> None:
        with self._get_connection() as con:
            con.execute(
                "UPDATE reminders SET status='fired' WHERE id=?",
                (rid,)
            )

    def _get_from_database(self, rid: int) -> str:
        with self._get_connection() as con:
            text = con.execute(
                "SELECT text FROM reminders WHERE id=?",
                (rid,)
            ).fetchone()[0]
            return text

    def _get_reminders(self) -> List[tuple]:
        with self._get_connection() as con:
            res = con.execute(
                "SELECT id, time, text, status FROM reminders WHERE status='scheduled' ",
            ).fetchall()
            return res

    def _load_reminders_from_database(self) -> None:
        with self._get_connection() as con:
            res = con.execute(
                "SELECT id, time FROM reminders WHERE status='scheduled' ",
            )
            for rid, rtime in res:
                self._schedule_reminder(rtime, rid)

    def start(self) -> None:
        self._load_reminders_from_database()
        self._cycle_thread = threading.Thread(
            target=self._worker,
            daemon=True,
        )
        self._cycle_thread.start()

    def stop(self):
        self._stop_event.set()
        self._queue_event.set()
        if self._cycle_thread is not None:
            self._cycle_thread.join()
        self._executor.shutdown(wait=True)

    def _schedule_reminder(self, rtime: float, rid: int) -> None:
        remaining_time = rtime - time.time()
        if remaining_time < 0:
            self._mark_fired_in_database(rid)
            return
        self._mark_planned_in_database(rid)
        with self._lock:
            heapq.heappush(self._queue, (remaining_time + time.time(), rid))
        self._queue_event.set()

    def _worker(self):
        while not self._stop_event.is_set():
            with self._lock:
                is_not_queue = not self._queue
            if is_not_queue:
                self._queue_event.wait()
                self._queue_event.clear()
                continue

            with self._lock:
                fire_time, rid = self._queue[0]
            delay = fire_time - time.time()

            if delay > 0:
                self._queue_event.wait(delay)
                self._queue_event.clear()
                continue

            with self._lock:
                heapq.heappop(self._queue)
            self._mark_executing_in_database(rid)
            threading.Thread(target=self._reminder_callback, args=(rid,)).start()

    def _reminder_callback(self, rid: int) -> None:
        print(self._get_from_database(rid), rid)
        self._mark_fired_in_database(rid)


    def add_reminder(self, rtime: float, text: str) -> None:
        rid = self._add_to_database(rtime, text)
        self._schedule_reminder(rtime, rid)
