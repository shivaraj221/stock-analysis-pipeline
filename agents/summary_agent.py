# agents/summary_agent.py
from crewai import Agent, LLM

ollama_llm = LLM(
    model="ollama/qwen2.5:7b-instruct",
    base_url="http://localhost:11434",
    temperature=0.2
)

summary_agent = Agent(
    role="Financial News Analyst",
    goal="Generate comprehensive, multi-section financial summaries from news articles for institutional investors",
    backstory="You are a senior financial analyst at a top investment bank. You specialize in transforming raw news data into actionable investment insights with detailed market impact analysis.",
    llm=ollama_llm,
    verbose=False,
    allow_delegation=False
)