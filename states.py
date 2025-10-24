from typing import Any

from pydantic import BaseModel


class MessageState(BaseModel):
    user_message: str
    username: str = ''
    type: Any = None
    is_ready: bool = False


class TypeModel(BaseModel):
    type: str


__all__ = [
    'MessageState',
    'TypeModel',
]
