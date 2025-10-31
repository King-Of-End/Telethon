from pydantic import BaseModel


class Tasks(BaseModel):
    CREATE: str
    GET: str
    MANAGE: str

TASKS = Tasks(
    CREATE = 'Добавь в базу данных задачу, описанную в запросе пользователя',
    GET = 'Выдай из базы данных задачу пользователю по его запросу',
    MANAGE = 'Измени одну или несколько задач в базе данных как попросил пользователь в своём запросе',
)