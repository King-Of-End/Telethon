from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_ollama import OllamaLLM, ChatOllama

from prompts import task_system_prompt
from tools import tools

load_dotenv()

local_llm = ChatOllama(
    model='gpt-oss:20b',
    temperature=0,
    reasoning=True,
    repeat_last_n=-1,
    base_url='http://star-curriculum.gl.at.ply.gg:58596'
)

agent_llm = ChatOllama(
    model='gpt-oss:20b',
    base_url='http://star-curriculum.gl.at.ply.gg:58596'
)

tooled_agent = create_agent(
    model=agent_llm,
    tools=tools,
    system_prompt=task_system_prompt,
)

base_llm = local_llm
tooled_llm = tooled_agent

__all__ = [
    'base_llm',
    'tooled_llm',
]
