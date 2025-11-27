from crewai import Agent, LLM
from tools.news_fetcher import NewsFetcherTool
from tools.news_summarizer import NewsSummarizerTool

ollama_llm = LLM(
    model="ollama/qwen2.5:7b-instruct",
    base_url="http://localhost:11434",
    temperature=0.1
)

news_agent = Agent(
    role="News Processing Agent",
    goal="Fetch latest market news for stock symbols and create a single comprehensive JSON file with all summaries",
    backstory="You fetch stock-related news from APIs, process them, and create one master file containing all news summaries for easy analysis.",
    tools=[
        NewsFetcherTool(),
        NewsSummarizerTool()
    ],
    llm=ollama_llm,
    verbose=False,
    allow_delegation=False
)