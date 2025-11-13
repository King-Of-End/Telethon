from typing import List, Literal, Callable, Any
from langchain_core.tools import StructuredTool
from langchain.tools import tool
import sqlite3

from qdrant import QDrantVectorDatabase

tools: List[StructuredTool] = list()
functions: dict[str, Callable] = dict()
database: QDrantVectorDatabase = QDrantVectorDatabase()
sql_db: str = 'databases/sqlite/tasks.sqlite'


def add(func: Any) -> Callable:
    tools.append(func)
    return func


def add_func(name: str) -> Callable:
    def add_func_wrapper(func: Any) -> Callable:
        functions[name] = func
        return func

    return add_func_wrapper


@add
@tool
@add_func('add_task')
def add_task(task: str,
             date: str,
             time: str,
             priority: int) -> Literal['Успешно', 'Неуспешно']:
    """Добавляет задачу в базу данных
    Входные данные:
    task: str (текст задачи)
    date: str (формат YYYY-MM-DD)
    time: str (формат HH:MM)
    priority: int (от 1 до 10)"""

    doc_id = database.add_task(task, date, time, priority)

    if doc_id is None:
        return 'Неуспешно'

    request: str = f'''INSERT INTO active_tasks(task, date, time, priority, doc_id) 
    VALUES("{task}", "{date}", "{time}", {priority}, "{doc_id}")'''

    try:
        con = sqlite3.connect(sql_db)
        cur = con.cursor()
        cur.execute(request)
        con.commit()
        return 'Успешно'
    except sqlite3.DatabaseError:
        database.delete_task(doc_id)
        return 'Неуспешно'


@add
@tool
@add_func('search_tasks_database')
def search_tasks_database(task: str | None = None,
                          date: str | None = None,
                          time: str | None = None,
                          priority: int | None = None) -> List[dict[str, str | int]] | Literal['Неуспешно']:
    """Производит поиск по базе данных принимая одно или несколько следующих значений
    Входные данные:
    task: str | None (текст задачи)
    date: str | None (формат YYYY-MM-DD)
    time: str | None (формат HH:MM)
    priority: int | None (от 1 до 10)
    Все входные данные должны соответствовать CRUD запросам к sqlite базам данных

    Возвращает список с результатами поиска """

    request: str = f'''SELECT task, date, time, priority FROM active_tasks '''
    if task: request += f'''{task=} '''
    if date: request += f'''{date=} '''
    if time: request += f'''{time=} '''
    if priority: request += f'''{priority=} '''

    try:
        con = sqlite3.connect(sql_db)
        cur = con.cursor()
        res = cur.execute(request).fetchall()
        ans: List[dict[str, str | int]] = list()
        for row in res:
            ans.append(dict(row))
        return ans
    except sqlite3.DatabaseError:
        return 'Неуспешно'


@add
@tool
@add_func('update_task')
def update_task(task_id: int,
                task: str | None = None,
                date: str | None = None,
                time: str | None = None,
                priority: int | None = None,) -> Literal['Успешно', 'Неуспешно']:
    """Обновляет данные задачи в базе данных по id
    Входные данные:
    Обязательные:
    task_id: int (идентификатор задачи)
    Опциональные:
    date: str | None (новая дата)
    task: str | None (новый текст задачи)
    time: str | None (новое время)
    priority: int | None (новый приоритет)

    Возвращает сообщение об успехе/неуспехе"""

    doc_id_request = f'''SELECT doc_id FROM active_tasks WHERE id={task_id}'''

    try:
        con = sqlite3.connect(sql_db)
        cur = con.cursor()
        doc_id = cur.execute(doc_id_request).fetchone()[0]
    except Exception:
        return 'Неуспешно'

    database.delete_task(doc_id[-1])
    database.add_task(task, date, time, priority)

    request: str = f'''UPDATE active_tasks 
    SET '''
    if date: request += f'''{date=} \n'''
    if task: request += f'''{task=} \n'''
    if priority: request += f'''{priority=} \n'''
    request += f'''WHERE id={task_id}'''

    try:
        con = sqlite3.connect(sql_db)
        cur = con.cursor()
        cur.execute(request)
        con.commit()
        database.delete_task(task_id)
        return 'Успешно'
    except sqlite3.DatabaseError:
        return 'Неуспешно'


@add
@tool
@add_func('delete_task')
def delete_task(task_id: int) -> Literal['Успешно', 'Неуспешно']:
    """Удаляёт задачу по id и убирает её в базу данных удаленных задач
    Входные данные:
    task_id: int (идентификатор задачи)

    Возвращает сообщение об успехе/неуспехе"""

    get_request: str = f'''SELECT * from active_tasks where id={task_id}'''
    del_request: str = f'''DELETE from active_tasks where id={task_id}'''

    try:
        con = sqlite3.connect(sql_db)
        cur = con.cursor()
        del_task = cur.execute(get_request).fetchone()
        database.delete_task(del_task[-1])
        add_request: str = f'''INSERT INTO deleted_tasks VALUES({del_task})'''
        cur.execute(add_request)
        cur.execute(del_request)
        con.commit()
        return 'Успешно'
    except sqlite3.DatabaseError:
        return 'Неуспешно'


@add
@tool
@add_func('search_similar')
def search_similar(query: str, top_k: int = 1) -> List[dict]:
    """Производит поиск по векторной базе данных с задачами
    Входные данные:
    query: str (запрос для поиска)
    top_k: int = 1 (необходимое количество полученных задач)

    Возвращает список с top_k количеством подходящих задач"""
    ans: List[dict] = []
    for i in database.get_task(query, top_k):
        ans.append(i.dict())
    return ans