from crewai import LLM
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL

ollama_llm = LLM(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.2,      # qwen likes low temp for accuracy
    max_tokens=4096
)
