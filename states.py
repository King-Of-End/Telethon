from pydantic import BaseModel


class MessageState(BaseModel):
    user_message: str
    username: str
    type: str
    is_ready: bool = False


class TypeModel(BaseModel):
    type: str


__all__ = [
    'MessageState',
    'TypeModel',
]
