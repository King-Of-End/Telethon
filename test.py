from langchain_ollama import OllamaLLM

llm = OllamaLLM(
    model='gpt-oss:20b',
    validate_model_on_init=True,
    base_url='http://star-curriculum.gl.at.ply.gg:58596/api'
)

print(llm.invoke('Привет!'))