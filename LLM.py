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

__all__ = [
    'base_local_llm',
    'base_global_llm',
]