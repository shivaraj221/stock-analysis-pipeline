from crewai import Agent, LLM
from tools.trending_scraper import TrendingStocksTool
from tools.yfinance_analyzer import YFinanceAnalysisTool
from llms.huggingface_llm import HuggingFaceLLM
from tools.classifier import StockClassifierTool
import os

# Use OpenRouter with OpenAI-compatible endpoint
hf_llm = HuggingFaceLLM(
    model="moonshotai/Kimi-K2-Thinking:novita",
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
    llm=hf_llm,
    verbose=False,
    allow_delegation=False,
    max_tokens=1000
)
