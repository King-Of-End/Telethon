from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel


class MessageState(BaseModel):
    message: str
    username: str
    type: str


# Создание узлов
def check_content(state: MessageState) -> MessageState:
    return state


def create_task(state: MessageState) -> MessageState:
    return state


def get_task(state: MessageState) -> MessageState:
    return state


def manage_task(state: MessageState) -> MessageState:
    return state


# Создание условных ребер
def task_distribution(state: MessageState) -> str:
    return state[type]


graph = StateGraph(MessageState)

graph.add_node('check_content', check_content)
graph.add_node('create_task', create_task)
graph.add_node('get_task', get_task)
graph.add_node('manage_task', manage_task)

graph.add_edge(START, 'check_content')
graph.add_conditional_edges(
    'check_content',
    task_distribution,
    {
        'create_task': 'create_task',
        'get_task': 'get_task',
        'manage_task': 'manage_task'
    }
)

app = graph.compile()
