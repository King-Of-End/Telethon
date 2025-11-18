from typing import List, Literal

from langchain_core.messages import BaseMessage, HumanMessage
from typing_extensions import TypedDict

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.tools import tool, StructuredTool
from llama_index.core import PromptTemplate
from pydantic import BaseModel


# 1. Создаем инструмент
def transform(a: int, b: int) -> int:
    """Transforms two numbers"""
    return a + b * 2



tools = [StructuredTool.from_function(transform)]

# 2. Инициализируем Ollama LLM
llm = ChatOllama(
    model="gpt-oss:20b",
    base_url="http://star-curriculum.gl.at.ply.gg:58596",
    temperature=0.7,
    reasoning=True
)

# 4. Создаем агента
agent = create_agent(
    model=llm,
    tools=tools,
)

user_input = HumanMessage('Привет! Какой результат трансформации 2 и 6?')

class InputState(BaseModel):
    messages: List[HumanMessage]


# 5. Используем агента
result = agent.invoke(InputState(messages=[user_input]))

print('=' * 50)
print(result['messages'][-1].content, '\n',
      result['messages'][-1].additional_kwargs['reasoning_content'])