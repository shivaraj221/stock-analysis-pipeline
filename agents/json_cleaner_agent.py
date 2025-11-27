from crewai import Agent, LLM
from tools.json_cleaner_tool import JSONCleanerTool

# GPT Model with your API key
gpt_llm = LLM(
    model="openai/gpt-3.5-turbo",
    api_key="OPENAI_API_KEY",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.1
)

json_cleaner_agent = Agent(
    role="JSON Cleaner",
    goal="Clean malformed JSON files and save corrected versions",
    backstory="Specialized agent for sanitizing JSON output from other pipelines.",
    tools=[JSONCleanerTool()],
    llm=gpt_llm,
    verbose=False,
    allow_delegation=False,
    max_tokens=1000
)
