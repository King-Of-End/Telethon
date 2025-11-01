import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI

load_dotenv()

base_local_llm = OllamaLLM(
    model='qwen3:8b',
    temperature=0,
    reasoning=True,
    repeat_last_n=-1,
)

base_global_llm = ChatOpenAI(
    model='qwen/qwen3-235b-a22b:free',
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
    reasoning_effort='high',
)

advanced_local_llm = OllamaLLM(
    model='gpt-oss:20b',
    temperature=0,
    reasoning=True,
    repeat_last_n=-1,
)

tooled_local_llm = OllamaLLM(
    model='qwen3:8b',
    temperature=0,
    reasoning=True,
    repeat_last_n=-1,
)

tooled_global_llm = ChatOpenAI(
    model='qwen/qwen3-235b-a22b:free',
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
    reasoning_effort='high',
)

is_llm_online = os.getenv('online')

base_llm = base_global_llm if is_llm_online else base_local_llm
advanced_llm = base_global_llm if is_llm_online else advanced_local_llm
tooled_llm = tooled_global_llm if is_llm_online else tooled_local_llm

__all__ = [
    'base_llm',
    'advanced_llm',
    'tooled_llm',
]
