from crewai import Agent, LLM
from tools.json_cleaner_tool import JSONCleanerTool

hf_llm = HuggingFaceLLM(
    model="moonshotai/Kimi-K2-Thinking:novita",
    temperature=0.1
)

json_cleaner_agent = Agent(
    role="JSON Cleaner",
    goal="Clean malformed JSON files and save corrected versions",
    backstory="Specialized agent for sanitizing JSON output from other pipelines.",
    tools=[JSONCleanerTool()],
    llm=hf_llm,
    verbose=False,
    allow_delegation=False,
    max_tokens=128
)
