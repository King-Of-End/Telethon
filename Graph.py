from langgraph.graph import StateGraph, START, END

import telegram
from tasks import TASKS
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
    state.chain.append('get_type')
    if state.completion is None:
        llm = base_local_llm
    else:
        llm = advanced_local_llm
    llm_chain = type_prompt | llm | type_parser
    res = llm_chain.invoke(input={'user_input': state.user_message})
    state.type = res['type']
    return state


def talk(state: MessageState) -> MessageState:
    state.chain.append('talk')
    res = advanced_local_llm.invoke(state.user_message)
    state.message = res
    return state


def create_task(state: MessageState) -> MessageState:
    state.chain.append('create_task')
    llm_chain = task_prompt | advanced_local_llm | task_parser
    res = llm_chain.invoke(input={'user_input': state.user_message, 'task': TASKS.CREATE})
    state.message = res['message']
    return state


def get_task(state: MessageState) -> MessageState:
    state.chain.append('get_task')
    llm_chain = task_prompt | advanced_local_llm | task_parser
    res = llm_chain.invoke(input={'user_input': state.user_message, 'task': TASKS.GET})
    state.message = res['message']
    return state


def manage_task(state: MessageState) -> MessageState:
    state.chain.append('manage_task')
    llm_chain = task_prompt | advanced_local_llm | task_parser
    res = llm_chain.invoke(input={'user_input': state.user_message, 'task': TASKS.MANAGE})
    state.message = res['message']
    return state


def get_completion(state: MessageState) -> MessageState:
    state.chain.append('get_completion')
    return state


def send_message(state: MessageState) -> MessageState:
    state.chain.append('send_message')
    telegram.send_message(state.message, state.username)
    return state


# Создание условных ребер
def check_type(state: MessageState) -> str:
    return state.type


def check_completion(state: MessageState) -> bool:
    return state.completion


graph = StateGraph(MessageState)

graph.add_node('get_type', get_type)

graph.add_node('create_task', create_task)
graph.add_node('get_task', get_task)
graph.add_node('manage_task', manage_task)
graph.add_node('talk', talk)

graph.add_node('get_completion', get_completion)
graph.add_node('send_message', send_message)

graph.add_edge(START, 'get_type')
graph.add_edge('create_task', 'get_completion')
graph.add_edge('get_task', 'get_completion')
graph.add_edge('manage_task', 'get_completion')
graph.add_edge('talk', 'get_completion')

graph.add_conditional_edges(
    'get_type',
    check_type,
    {
        'talk': 'talk',
        'add': 'create_task',
        'get': 'get_task',
        'manage': 'manage_task',
    }
)

graph.add_conditional_edges(
    'get_completion',
    check_completion,
    {
        None: 'send_message',
        False: 'get_type'
    }
)

app = graph.compile()

if __name__ == '__main__':
    print_graph()
