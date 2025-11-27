from crewai import Agent, LLM
from tools.json_cleaner_tool import JSONCleanerTool

ollama_llm = LLM(
    model="ollama/qwen2.5:7b-instruct",
    base_url="http://localhost:11434",
    temperature=0.1
)

json_cleaner_agent = Agent(
    role="JSON Cleaner",
    goal="Clean malformed JSON files and save corrected versions",
    backstory="Specialized agent for sanitizing JSON output from other pipelines.",
    tools=[JSONCleanerTool()],
    llm=ollama_llm,
    verbose=False,
    allow_delegation=False,
    max_tokens=128
)
