from crewai import Agent, LLM
from tools.trending_scraper import TrendingStocksTool
from tools.yfinance_analyzer import YFinanceAnalysisTool
from tools.classifier import StockClassifierTool

# Free Gemma model - NO API KEY NEEDED
gemma_llm = LLM(
    model="google/gemma-3-4b-it:free",
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
    llm=gemma_llm,
    verbose=False,
    allow_delegation=False,
    max_tokens=1000
)
