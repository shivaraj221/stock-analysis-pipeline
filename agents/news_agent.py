from crewai import Agent, LLM
from tools.news_fetcher import NewsFetcherTool
from tools.news_summarizer import NewsSummarizerTool

# GPT Model with your API key
gpt_llm = LLM(
    model="google/gemma-3-4b-it:free",
    api_key="OPENAI_API_KEY",
    base_url="https://openrouter.ai/api/v1",
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
    llm=gpt_llm,
    verbose=False,
    allow_delegation=False,
    max_tokens=1000
)
