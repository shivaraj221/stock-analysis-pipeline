# config.py
from crewai import LLM

ollama_llm = LLM(
    model="ollama/qwen2.5:7b-instruct",
    base_url="http://localhost:11434",
    temperature=0.1,
    timeout=600
)