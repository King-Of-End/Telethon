from langchain_ollama import OllamaLLM

base_llm = OllamaLLM(
    model='qwen3:8b',
    temperature=0
)

