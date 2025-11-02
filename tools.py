from typing import List, Optional, Literal, Callable, Any
from langchain_core.tools import StructuredTool
from langchain.tools import tool
import sqlite3

tools: List[StructuredTool] = list()
functions: List[Callable] = list()


def add(func: Any) -> Callable:
    tools.append(func)
    return func


def add_func(func: Any) -> Callable:
    functions.append(func)
    return func


@add
@tool
@add_func
def add_task(date: str, title: str, priority: int) -> Literal['Успешно', 'Неуспешно']:
    """Добавляет задачу в базу данных
    Входные данные:
    date: str (формат YYYY-MM-DD)
    task: str (текст задачи)
    priority: int (от 1 до 10)"""

    request: str = f'''INSERT INTO active_tasks(date, title, priority) 
    VALUES({date}, {title}, {priority})'''

    try:
        con = sqlite3.connect('tasks.sqlite')
        cur = con.cursor()
        cur.execute(request)
        con.commit()
        return 'Успешно'
    except sqlite3.DatabaseError:
        return 'Неуспешно'


@add
@tool
@add_func
def search_tasks_database(date: Optional[str], task: Optional[str], priority: Optional[str]) \
        -> List[dict[str, str | int]]:
    """Производит поиск по базе данных принимая одно или несколько следующих значений
    Входные данные:
    date: str (формат YYYY-MM-DD)
    task: str (текст задачи)
    priority: str (от 1 до 10)
    Все входные данные должны соответствовать CRUD запросам к sqlite базам данных

    Возвращает список с результатами поиска """


@add
@tool
@add_func
def update_task(task_id: int, date: Optional[str], task: Optional[str], priority: Optional[str]) \
        -> Literal['Успешно', 'Неуспешно']:
    """Обновляет данные задачи в базе данных по id
    Входные данные:
    Обязательные:
    task_id: int (идентификатор задачи)
    Опциональные:
    date: Optional[str] (новая дата)
    task: Optional[str] (новый текст задачи)
    priority: Optional[str] (новый приоритет)

    Возвращает сообщение об успехе/неуспехе"""


@add
@tool
@add_func
def delete_task(task_id: int) -> Literal['Успешно', 'Неуспешно']:
    """Удаляёт задачу по id и убирает её в базу данных удаленных задач
    Входные данные:
    task_id: int (идентификатор задачи)

    Возвращает сообщение об успехе/неуспехе"""

    get_request: str = f'''SELECT from active_tasks where id={task_id}'''
    del_request: str = f'''DELETE from active_tasks where id={task_id}'''

    try:
        con = sqlite3.connect('tasks.sqlite')
        cur = con.cursor()
        task = cur.execute(get_request).fetchall()
        add_request: str = f'''INSERT INTO deleted_tasks VALUES({task[0]})'''
        cur.execute(add_request)
        cur.execute(del_request)
        con.commit()
        return 'Успешно'
    except sqlite3.DatabaseError:
        return 'Неуспешно'


@add
@tool
@add_func
def search_similar(query: str, top_k: Optional[int] = 1) -> List[dict]:
    """Производит поиск по векторной базе данных с задачами
    Входные данные:
    query: str (запрос для поиска)
    top_k: Optional[int] = 1 (необходимое количество полученных задач)

    Возвращает список с top_k количеством подходящих задач"""
