from typing import List

from pydantic import BaseModel


class MessageState(BaseModel):
    user_message: str
    username: str = ''
    type: str = ''
    completion: bool | None = None
    message: str = ''
    chain: List[str] = list()


class TypeModel(BaseModel):
    type: str


class TaskModel(BaseModel):
    message: str


__all__ = [
    'MessageState',
    'TypeModel',
    'TaskModel',
]
