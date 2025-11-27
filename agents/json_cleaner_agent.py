from crewai import Agent, LLM
from tools.json_cleaner_tool import JSONCleanerTool

gemma_llm = LLM(
    model="google/gemma-3-4b-it:free",
    base_url="https://openrouter.ai/api/v1",
    api_key="null",  # Free models don't need key, but CrewAI requires this field
    temperature=0.1
)

json_cleaner_agent = Agent(
    role="JSON Cleaner",
    goal="Clean malformed JSON files and save corrected versions",
    backstory="Specialized agent for sanitizing JSON output from other pipelines.",
    tools=[JSONCleanerTool()],
    llm=gemma_llm,
    verbose=False,
    allow_delegation=False,
    max_tokens=1000
)
