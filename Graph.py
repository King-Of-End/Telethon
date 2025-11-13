import asyncio

from langgraph.graph import StateGraph, START, END

from tasks import TASKS
from LLM import *
from prompts import *
from parsers import *


# Сделать рисунок графа
def print_graph():
    with open('graph.png', "wb") as f:
        f.write(app.get_graph().draw_mermaid_png())

def kprint(st):
    print(st)
    return st


# Создание узлов
def get_type(state: MessageState) -> MessageState:
    state.chain.append('get_type')
    llm = base_llm
    llm_chain = type_prompt | llm | type_parser
    res = llm_chain.invoke(input={'user_input': state.user_message})
    state.type = res['type']
    return state


def talk(state: MessageState) -> MessageState:
    state.chain.append('talk')
    res = base_llm.invoke(state.user_message)
    state.message = res
    return state


async def create_task(state: MessageState) -> MessageState:
    state.chain.append('create_task')
    prompt = str(task_human_prompt.invoke(input={'user_input': state.user_message, 'task': TASKS.CREATE}))
    r_res =  str(await tooled_llm.run(prompt))
    res = task_parser.invoke(r_res)
    state.message = res['message']
    return state


async def get_task(state: MessageState) -> MessageState:
    state.chain.append('get_task')
    prompt = str(task_human_prompt.invoke(input={'user_input': state.user_message, 'task': TASKS.GET}))
    r_res =  str(await tooled_llm.run(prompt))
    res = task_parser.invoke(r_res)
    state.message = res['message']
    return state


async def manage_task(state: MessageState) -> MessageState:
    prompt = str(task_human_prompt.invoke(input={'user_input': state.user_message, 'task': TASKS.MANAGE}))
    r_res =  str(await tooled_llm.run(prompt))
    res = task_parser.invoke(r_res)
    state.message = res['message']
    return state


def get_completion(state: MessageState) -> MessageState:
    state.chain.append('get_completion')
    return state


def send_message(state: MessageState) -> MessageState:
    state.chain.append('send_message')
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

async def main():
    init = MessageState(user_message='Удали задачу посмотреть ютуб',)

    raw_answer = await app.ainvoke(init)
    result = MessageState(**raw_answer)

    print(result.message)
    print(result)

if __name__ == '__main__':
    asyncio.run(main())