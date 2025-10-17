from langgraph.graph import StateGraph
from pydantic import BaseModel


class MessageState(BaseModel):
    message: str
    username: str


class MyGraph:
    def __init__(self):
        self.graph = StateGraph(MessageState)
