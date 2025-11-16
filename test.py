from typing import List, Literal

from langchain_core.messages import BaseMessage, HumanMessage
from typing_extensions import TypedDict

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.tools import tool
from llama_index.core import PromptTemplate
from pydantic import BaseModel


# 1. Создаем инструмент
@tool
def search(query: str) -> str:
    """Search for information online"""
    return f"Search results for: {query}"

tools = [search]

# 2. Инициализируем Ollama LLM
llm = ChatOllama(
    model="gpt-oss:20b",
    base_url="http://star-curriculum.gl.at.ply.gg:58596",
    temperature=0.7
)

# 4. Создаем агента
agent = create_agent(
    model=llm,
    tools=tools,
)

user_input = HumanMessage('Привет')

class InputState(BaseModel):
    messages: List[HumanMessage]


# 5. Используем агента
result = agent.invoke(InputState(messages=[user_input]))

print(result)