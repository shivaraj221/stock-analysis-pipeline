from crewai import Agent, LLM
from tools.trending_scraper import TrendingStocksTool
from tools.yfinance_analyzer import YFinanceAnalysisTool
from tools.classifier import StockClassifierTool

# GPT Model with your API key
gpt_llm = LLM(
    model="openai/gpt-3.5-turbo",
    api_key="OPENAI_API_KEY",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.1
)

toolchain_agent = Agent(
    role="Full Pipeline Executor",
    goal="Scrape → Analyze → Classify → Save JSON",
    backstory="Runs all 3 tools in order. No delegation. No talking.",
    tools=[
        TrendingStocksTool(),
        YFinanceAnalysisTool(),
        StockClassifierTool(),
    ],
    llm=gpt_llm,
    verbose=False,
    allow_delegation=False,
    max_tokens=1000
)
