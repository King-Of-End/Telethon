from typing import List, Literal, Callable, Any
import sqlite3
from llama_index.core.tools import FunctionTool

tools = list()
functions: dict[str, Callable] = dict()
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

    # doc_id = database.add_task(task, date, time, priority)
    #
    # if doc_id is None:
    #     return 'Неуспешно'

    request: str = f'''INSERT INTO active(task, date, time, priority) 
    VALUES("{task}", "{date}", "{time}", {priority})'''

    try:
        con = sqlite3.connect(sql_db)
        cur = con.cursor()
        cur.execute(request)
        con.commit()
        con.close()
        return 'Успешно'
    except sqlite3.DatabaseError:
        # database.delete_task(doc_id)
        return 'Неуспешно'


@add_func
def search_tasks_database(task: str | None = None,
                          date: list | None = None,
                          time: str | None = None,
                          priority: list | None = None
                          ) -> List[tuple] | Literal['Неуспешно']:
    """Производит поиск по базе данных принимая одно или несколько следующих значений
    Входные данные:
    task: str | None (текст задачи)
    date: list | None (список: [дата_от, дата_до, '>'] или дата строкой)
    time: str | None (формат HH:MM)
    priority: list | None (список: [приоритет_от, приоритет_до, '>'] или число)

    Возвращает список с результатами поиска """

    request: str = f'''SELECT id, task, date, time, priority FROM active '''
    conditions = []

    if task:
        conditions.append(f'''task LIKE "%{task}%"''')

    if date:
        if isinstance(date, list) and len(date) == 3 and date[2] == '>':
            conditions.append(f'''date >= "{date[0]}" AND date <= "{date[1]}"''')
        elif isinstance(date, str):
            conditions.append(f'''date = "{date}" ''')

    if time:
        conditions.append(f'''time = "{time}" ''')

    if priority:
        if isinstance(priority, list) and len(priority) == 3 and priority[2] == '>':
            conditions.append(f'''priority >= {priority[0]} AND priority <= {priority[1]}''')
        elif isinstance(priority, int):
            conditions.append(f'''priority = {priority}''')

    if conditions:
        request += 'WHERE ' + ' AND '.join(conditions)

    print(request)

    try:
        con = sqlite3.connect(sql_db)
        cur = con.cursor()
        res = cur.execute(request).fetchall()
        con.close()
        return res
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        return 'Неуспешно'


@add_func
def update_task(task_id: int,
                task: str | None = None,
                date: str | None = None,
                time: str | None = None,
                priority: int | None = None) -> Literal['Успешно', 'Неуспешно']:
    """Обновляет данные задачи в базе данных по id
    Входные данные:
    Обязательные:
    task_id: int (идентификатор задачи)
    Опциональные:
    task: str | None (новый текст задачи)
    date: str | None (новая дата)
    time: str | None (новое время)
    priority: int | None (новый приоритет)

    Возвращает сообщение об успехе/неуспехе"""

    try:
        con = sqlite3.connect(sql_db)
        cur = con.cursor()

        # Получаем текущие данные задачи
        get_request = f'''SELECT task, date, time, priority FROM active WHERE id={task_id}'''

        print(get_request)

        current_data = cur.execute(get_request).fetchone()

        if not current_data:
            con.close()
            return 'Неуспешно'

        current_task, current_date, current_time, current_priority = current_data

        # Используем текущие значения, если новые не указаны
        new_task = task if task else current_task
        new_date = date if date else current_date
        new_time = time if time else current_time
        new_priority = priority if priority else current_priority

        # Удаляем старый документ из векторной БД
        # database.delete_task(doc_id)

        # Добавляем новый документ в векторную БД
        # new_doc_id = database.add_task(new_task, new_date, new_time, new_priority)
        #
        # if new_doc_id is None:
        #     con.close()
        #     return 'Неуспешно'

        # Обновляем данные в SQL БД
        update_request = f'''UPDATE active 
        SET task="{new_task}", date="{new_date}", time="{new_time}", priority={new_priority}
        WHERE id={task_id}'''

        print(update_request)

        cur.execute(update_request)
        con.commit()
        con.close()

        return 'Успешно'

    except Exception as e:
        print(e)
        return 'Неуспешно'


@add_func
def delete_task(task_id: int) -> Literal['Успешно', 'Неуспешно']:
    """Удаляёт задачу по id и убирает её в базу данных удаленных задач
    Входные данные:
    task_id: int (идентификатор задачи)

    Возвращает сообщение об успехе/неуспехе"""

    try:
        con = sqlite3.connect(sql_db)
        cur = con.cursor()

        # Получаем данные задачи
        get_request = f'''SELECT id, task, date, time, priority FROM active WHERE id={task_id}'''
        del_task = cur.execute(get_request).fetchone()

        if not del_task:
            con.close()
            return 'Неуспешно'

        # Удаляем из векторной БД
        # database.delete_task(del_task[5])  # doc_id находится на 5-й позиции

        # Добавляем в таблицу deleted
        add_request = f'''INSERT INTO deleted(old_id, task, date, time, priority) 
                         VALUES({del_task[0]}, "{del_task[1]}", "{del_task[2]}", "{del_task[3]}", {del_task[4]} )'''
        print(add_request)
        cur.execute(add_request)

        # Удаляем из active
        del_request = f'''DELETE FROM active WHERE id={task_id} '''
        print(del_request)
        cur.execute(del_request)

        con.commit()
        con.close()

        return 'Успешно'

    except Exception as e:
        print(f"Error deleting task: {e}")
        return 'Неуспешно'


@add_func
def search_similar(query: str, top_k: int = 1) -> List[dict]:
    """Производит поиск по векторной базе данных с задачами
    Входные данные:
    query: str (запрос для поиска)
    top_k: int = 1 (необходимое количество полученных задач)

    Возвращает список с top_k количеством подходящих задач"""
    ans: List[dict] = []
    try:
        results = (query, top_k)
        for i in results:
            ans.append(i.dict())
        return ans
    except Exception as e:
        print(f"Error in search_similar: {e}")
        return []


def create_clear_db():
    con = sqlite3.connect(sql_db)
    cur = con.cursor()
    cur.execute('''CREATE TABLE active (
    id       INTEGER PRIMARY KEY AUTOINCREMENT
                     UNIQUE
                     NOT NULL,
    task     TEXT    NOT NULL,
    date     TEXT,
    time     TEXT,
    priority INTEGER NOT NULL
);
''')
    cur.execute('''CREATE TABLE deleted (
    id       INTEGER PRIMARY KEY AUTOINCREMENT
                     UNIQUE
                     NOT NULL,
    old_id   INTEGER NOT NULL,
    task     TEXT    NOT NULL,
    date     TEXT,
    time     TEXT,
    priority INTEGER NOT NULL
);
''')


__all__ = ['tools', 'functions', 'create_clear_db']