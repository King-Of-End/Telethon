import asyncio

from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import FunctionAgent

from prompts import task_system_prompt
from tools import tools

load_dotenv()

local_llm = OllamaLLM(
    model='gpt-oss:20b',
    temperature=0,
    reasoning=True,
    repeat_last_n=-1,
    base_url='http://star-curriculum.gl.at.ply.gg:58596'
)

agent_llm = Ollama(
    model='qwen3:8b',
)

tooled_agent = FunctionAgent(
    name='CoderAgent',
    description='This AI agent can generate professional-level code',
    system_prompt=task_system_prompt,
    streaming=False,
    llm=agent_llm,
    tools=tools)

base_llm = local_llm
tooled_llm = tooled_agent

__all__ = [
    'base_llm',
    'tooled_llm',
]

async def main():
    await tooled_llm.run('привет')

if __name__ == '__main__':
    asyncio.run(main())