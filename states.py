from typing import Any
from pydantic import BaseModel


class MessageState(BaseModel):
    user_message: str
    username: str = ''
    type: Any = None
    is_ready: bool = False
    message: str = ''


class TypeModel(BaseModel):
    type: str


class TaskModel(BaseModel):
    message: str


__all__ = [
    'MessageState',
    'TypeModel',
    'TaskModel',
]
