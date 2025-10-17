from typing import Tuple

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel


class MessageState(BaseModel):
    message: str
    username: str
    type: str
    is_ready: bool = False


# Создание узлов
def get_content(state: MessageState) -> MessageState:
    return state


def create_task(state: MessageState) -> MessageState:
    return state


def get_task(state: MessageState) -> MessageState:
    return state


def manage_task(state: MessageState) -> MessageState:
    return state


def get_completion(state: MessageState) -> MessageState:
    return state


# Создание условных ребер
def check_content(state: MessageState) -> str:
    return state.type


def check_completion(state: MessageState) -> Tuple[bool, str]:
    return state.is_ready, state.type


graph = StateGraph(MessageState)

graph.add_node('get_content', get_content)
graph.add_node('create_task', create_task)
graph.add_node('get_task', get_task)
graph.add_node('manage_task', manage_task)
graph.add_node('get_completion', get_completion)

graph.add_edge(START, 'get_content')
graph.add_edge('create_task', 'get_completion')
graph.add_edge('get_task', 'get_completion')
graph.add_edge('manage_task', 'get_completion')

graph.add_conditional_edges(
    'get_content',
    check_content,
    {
        'create_task': 'create_task',
        'get_task': 'get_task',
        'manage_task': 'manage_task'
    }
)
graph.add_conditional_edges(
    'get_completion',
    check_completion,
    {
        (True, 'create_task'): END,
        (True, 'get_task'): END,
        (True, 'manage_task'): END,
        (False, 'create_task'): 'create_task',
        (False, 'get_task'): 'get_task',
        (False, 'manage_task'): 'manage_task'
    }
)

app = graph.compile()

with open('graph.png', "wb") as f:
    f.write(app.get_graph().draw_mermaid_png())