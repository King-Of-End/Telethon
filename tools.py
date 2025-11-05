from typing import List, Optional, Literal, Callable, Any
from langchain_core.tools import StructuredTool
from langchain.tools import tool
import sqlite3

tools: List[StructuredTool] = list()
functions: dict[str: Callable] = dict()


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
def add_task(date: str, task: str, priority: int) -> Literal['Успешно', 'Неуспешно']:
    """Добавляет задачу в базу данных
    Входные данные:
    date: str (формат YYYY-MM-DD)
    task: str (текст задачи)
    priority: int (от 1 до 10)"""

    request: str = f'''INSERT INTO active_tasks(date, task, priority) 
    VALUES({date}, {task}, {priority})'''

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
@add_func('search_tasks_database')
def search_tasks_database(date: Optional[str] = None, task: Optional[str] = None, priority: Optional[str] = None) \
        -> List[dict[str, str | int]] | Literal['Неуспешно']:
    """Производит поиск по базе данных принимая одно или несколько следующих значений
    Входные данные:
    date: str (формат YYYY-MM-DD)
    task: str (текст задачи)
    priority: str (от 1 до 10)
    Все входные данные должны соответствовать CRUD запросам к sqlite базам данных

    Возвращает список с результатами поиска """

    request: str = f'''SELECT date, task, priority FROM active_tasks '''
    if date: request += f'''{date=} '''
    if task: request += f'''{task=} '''
    if priority: request += f'''{priority=} '''

    try:
        con = sqlite3.connect('tasks.sqlite')
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
def update_task(task_id: int, date: Optional[str] = None, task: Optional[str] = None, priority: Optional[str] = None) \
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

    request: str = f'''UPDATE active_tasks 
    SET '''
    if date: request += f'''{date=} \n'''
    if task: request += f'''{task=} \n'''
    if priority: request += f'''{priority=} \n'''
    request += f'''WHERE id={task_id}'''

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
@add_func('delete_task')
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
        del_task = cur.execute(get_request).fetchall()
        add_request: str = f'''INSERT INTO deleted_tasks VALUES({del_task[0]})'''
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
    top_k: Optional[int] = 1 (необходимое количество полученных задач)

    Возвращает список с top_k количеством подходящих задач"""
