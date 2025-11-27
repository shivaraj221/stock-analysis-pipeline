# test.py — FINAL FIXED VERSION FOR CREWAI 1.6.0
from crewai import Agent, Task, Crew, LLM
from tools.trending_scraper import TrendingStocksTool
from tools.yfinance_analyzer import YFinanceAnalysisTool
from tools.classifier import StockClassifierTool
import os

# Ollama LLM
ollama_llm = LLM(
    model="ollama/qwen2.5:7b-instruct",
    base_url="http://localhost:11434",
    temperature=0.1
)

os.makedirs("data", exist_ok=True)

agent = Agent(
    role="Pipeline Master",
    goal="Run scraper → analyzer → classifier → save JSON",
    backstory="You call the 3 tools in order. No talking. No excuses.",
    tools=[
        TrendingStocksTool(),
        YFinanceAnalysisTool(),
        StockClassifierTool()
    ],
    llm=ollama_llm,
    verbose=True,  # Boolean: True for verbose output
    allow_delegation=False
)

task = Task(
    description="Run full pipeline: scrape top gainers → analyze → classify → save to data/classified_stocks.json",
    expected_output="SUCCESS",
    agent=agent,
    output_file="data/classified_stocks.json",
    async_execution=False
)

print("RUNNING FULL PIPELINE...")
crew = Crew(
    tasks=[task], 
    verbose=True,  # FIXED: Boolean True/False only — no numbers like 2
    memory=False   # Disables memory for faster runs
)
result = crew.kickoff()

print("\n" + "="*60)
print("FINAL RESULT →", result)
print("FILE CREATED → data/classified_stocks.json")
print("OPEN IT NOW!")
print("="*60)