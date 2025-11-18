from typing import List

from pydantic import BaseModel
from typing_extensions import TypedDict


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

class Message(TypedDict):
    role: str
    content: str

class AgentInput(BaseModel):
    messages: List[Message]

__all__ = [
    'MessageState',
    'TypeModel',
    'TaskModel',
    'Message',
    'AgentInput',
]
