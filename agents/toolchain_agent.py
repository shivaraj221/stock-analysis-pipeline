from crewai import Agent, LLM
from tools.trending_scraper import TrendingStocksTool
from tools.yfinance_analyzer import YFinanceAnalysisTool
from tools.classifier import StockClassifierTool

# Try different free models - LiteLLM works better with some
gemma_llm = LLM(
    model="huggingface/google/gemma-3-4b-it:free",  # Different format
    base_url="https://openrouter.ai/api/v1",
    temperature=0.1
)

# Alternative models to try:
# model="meta-llama/llama-3.1-8b-instruct:free"
# model="microsoft/wizardlm-2-8x22b:free" 
# model="qwen/qwen-2.5-7b-instruct:free"

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
