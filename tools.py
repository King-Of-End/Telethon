from typing import List, Literal, Callable, Any
import sqlite3
from llama_index.core.tools import FunctionTool
from qdrant import QDrantVectorDatabase

tools = list()
functions: dict[str, Callable] = dict()
database: QDrantVectorDatabase = QDrantVectorDatabase()
sql_db: str = 'databases/sqlite/tasks.sqlite'


def add(func: Any) -> Callable:
    tools.append(func)
    return func


def add_func(func: Any) -> Callable:
    functions[func.__name__] = func
    tools.append(
        FunctionTool.from_defaults(
        fn=func,
        description=func.__doc__,
        name=func.__name__,
    ))
    return func


@add_func
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

    request: str = f'''INSERT INTO active(task, date, time, priority, doc_id) 
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

@add_func
def search_tasks_database(task: str | None = None,
                          date: str | None = None,
                          time: str | None = None,
                          priority: int | list | None = None
                          ) -> List[dict[str, str | int]] | Literal['Неуспешно']:
    """Производит поиск по базе данных принимая одно или несколько следующих значений
    Входные данные:
    task: str | None (текст задачи)
    date: str | None (формат YYYY-MM-DD)
    time: str | None (формат HH:MM)
    priority: int | None (от 1 до 10)
    Все входные данные должны соответствовать CRUD запросам к sqlite базам данных

    Возвращает список с результатами поиска """

    request: str = f'''SELECT task, date, time, priority FROM active '''
    if task or date or time or priority: request += 'WHERE '
    if task: request += f''' {task=} AND'''
    if date:
        if '>' not in date:
            request += f''' {date=} AND'''
        else:
            request += f''' date>{date[0]} AND date<{date[1]} AND'''
    if time: request += f''' {time=} AND'''
    if priority:
        if '>' not in priority:
            request += f''' {priority=} '''
        else:
            request += f''' priority>{priority[0]} AND priority<{priority[1]} '''

    request = request.strip('AND') + ' '

    try:
        con = sqlite3.connect(sql_db)
        cur = con.cursor()
        res = cur.execute(request).fetchall()
        ans: List[dict[str, str | int]] = list()
        for row in res:
            ans.append(dict(row))
        return ans
    except sqlite3.DatabaseError as e:
        a = e
        return 'Неуспешно'


@add_func
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

    doc_id_request = f'''SELECT doc_id FROM active WHERE id={task_id}'''

    try:
        con = sqlite3.connect(sql_db)
        cur = con.cursor()
        doc_id = cur.execute(doc_id_request).fetchone()[0]
    except Exception:
        return 'Неуспешно'

    database.delete_task(doc_id[-1])
    database.add_task(task, date, time, priority)

    request: str = f'''UPDATE active 
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


@add_func
def delete_task(task_id: int) -> Literal['Успешно', 'Неуспешно']:
    """Удаляёт задачу по id и убирает её в базу данных удаленных задач
    Входные данные:
    task_id: int (идентификатор задачи)

    Возвращает сообщение об успехе/неуспехе"""

    get_request: str = f'''SELECT * from active where id={task_id}'''
    del_request: str = f'''DELETE from active where id={task_id}'''

    try:
        con = sqlite3.connect(sql_db)
        cur = con.cursor()
        del_task = cur.execute(get_request).fetchone()
        database.delete_task(del_task[-1])
        add_request: str = f'''INSERT INTO deleted VALUES({del_task})'''
        cur.execute(add_request)
        cur.execute(del_request)
        con.commit()
        return 'Успешно'
    except sqlite3.DatabaseError:
        return 'Неуспешно'


@add_func
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


