from pydantic import BaseModel
from langgraph.graph import StateGraph, END, START


class TestState(BaseModel):
    name: str
    address: str

def capitalize_name(state: TestState) -> TestState:
    state.name = state.name.capitalize()
    return state

def print_info(state: TestState) -> TestState:
    print(state.name)
    print(state.address)
    return state

graph = StateGraph(TestState)

graph.add_node('capitalize_name', capitalize_name)
graph.add_node('print_info', print_info)

graph.add_edge(START, 'capitalize_name')
graph.add_edge('capitalize_name', 'print_info')
graph.add_edge('print_info', END)

app = graph.compile()
app.invoke(TestState(name='nikita', address='moscow'))
