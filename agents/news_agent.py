from crewai import Agent, LLM
from tools.news_fetcher import NewsFetcherTool
from tools.news_summarizer import NewsSummarizerTool
from llm.huggingface_llm import HuggingFaceLLM


# Free Gemma model - NO API KEY NEEDED
hf_llm = HuggingFaceLLM(
    model="moonshotai/Kimi-K2-Thinking:novita",
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
    llm=hf_llm,
    verbose=False,
    allow_delegation=False,
    max_tokens=1000
)
