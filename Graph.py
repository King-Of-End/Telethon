from typing import Tuple
from langgraph.graph import StateGraph, START, END

import telegram
from tasks import tasks
from states import *
from LLM import *
from prompts import *
from parsers import *


# Сделать рисунок графа
def print_graph():
    with open('graph.png', "wb") as f:
        f.write(app.get_graph().draw_mermaid_png())


# Создание узлов
def get_type(state: MessageState) -> MessageState:
    llm_chain = type_prompt | base_global_llm | type_parser
    res = llm_chain.invoke(input={'user_input': state.user_message})
    state.type = res
    return state


def create_task(state: MessageState) -> MessageState:
    llm_chain = create_task_prompt | base_global_llm | task_parser
    res = llm_chain.invoke(input={'user_input': state.user_message, 'task': tasks['create']})
    state.message = res
    return state


def get_task(state: MessageState) -> MessageState:
    return state


def manage_task(state: MessageState) -> MessageState:
    return state


def get_completion(state: MessageState) -> MessageState:
    return state


def send_message(state: MessageState) -> MessageState:
    telegram.send_message(state.message, state.username)
    return state


# Создание условных ребер
def check_type(state: MessageState) -> str:
    return state.type


graph = StateGraph(MessageState)

graph.add_node('get_content', get_type)
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
    check_type,
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
