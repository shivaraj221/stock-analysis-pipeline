# tasks/toolchain_task.py
from crewai import Task
from agents.toolchain_agent import toolchain_agent
import os
os.makedirs("data", exist_ok=True)

toolchain_task = Task(
    description=(
        "Execute the following steps strictly in order:\n"
        "1. Call trending_stocks_tool with limit=5.\n"
        " This must save the file at:\n"
        " C:/Users/Admin/Desktop/crewai-1/crewai/data/top_gainers.json\n\n"
        "2. After step 1 completes, call yfinance_analysis_tool.\n"
        " This must load top_gainers.json and save output to:\n"
        " C:/Users/Admin/Desktop/crewai-1/crewai/data/stock_analysis.json\n\n"
        "3. After step 2 completes, call stock_classifier_tool.\n"
        " This must load stock_analysis.json and save output to:\n"
        " C:/Users/Admin/Desktop/crewai-1/crewai/data/classified_stocks.json\n\n"
        
        "IMPORTANT RULES:\n"
        "- Do NOT generate any data yourself.\n"
        "- Do NOT hallucinate stock lists.\n"
        "- Only call the tools.\n"
        "- After all 3 tools run successfully, reply ONLY with: SUCCESS."
    ),
    expected_output=(
        "Stock classification analysis completed with BUY/SELL/HOLD recommendations. "
        "The output file contains comprehensive analysis including:\n"
        "- Stock symbols with action recommendations (STRONG BUY 🚀, BUY 📈, HOLD ⚖️, CAUTIOUS ⚠️, SELL 📉)\n"
        "- Total investment scores and confidence levels\n"
        "- Category breakdowns (valuation, growth, momentum, financial health, market position)\n"
        "- Key strengths and concerns for each stock\n"
        "- Investment thesis explaining the recommendation\n"
        "- Analysis timestamp and IPO status detection\n"
        "File saved to: C:/Users/Admin/Desktop/crewai-1/crewai/data/new_classified_stocks.json"
    ),
    agent=toolchain_agent,
    output_file="data/new_classified_stocks.json",
    async_execution=False
)