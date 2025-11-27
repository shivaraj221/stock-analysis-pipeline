from crewai import Agent, LLM
from tools.json_cleaner_tool import JSONCleanerTool

llama_llm = LLM(
    model="meta-llama/llama-3.1-8b-instruct:free",
    base_url="https://openrouter.ai/api/v1", 
    api_key="null",
    temperature=0.1
)

json_cleaner_agent = Agent(
    role="JSON Cleaner",
    goal="Clean malformed JSON files and save corrected versions",
    backstory="Specialized agent for sanitizing JSON output from other pipelines.",
    tools=[JSONCleanerTool()],
    llm=gllama_llm,
    verbose=False,
    allow_delegation=False,
    max_tokens=1000
)
