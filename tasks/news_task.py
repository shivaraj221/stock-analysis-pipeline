# tasks/news_task.py
from crewai import Task
from agents.news_agent import news_agent

news_task = Task(
    description="""
You must execute the **full news pipeline** in the correct sequence.

-----------------------------------------------
STEP 1 — FETCH LATEST NEWS
-----------------------------------------------
• Call: news_fetcher_tool
• Fetch news for every symbol in data/top_gainers.json
• Save raw results into: data/news/<SYMBOL>_news.json

-----------------------------------------------
STEP 2 — BUILD ONE MASTER NEWS FILE
-----------------------------------------------
• Call: news_summarizer_tool
• Read ALL files inside data/news/
• Extract:
    - title
    - description
    - source
    - publishedAt
    - url
• Build a SINGLE organized JSON output:
      data/all_news_summaries.json

-----------------------------------------------
REQUIREMENTS
-----------------------------------------------
• DO NOT generate analysis or LLM summaries here.
• DO NOT skip any stock.
• Output must contain ALL stocks and ALL articles.
• The summarizer tool should create a complete, clean,
  structured master JSON file ready for the next LLM step.

-----------------------------------------------
YOUR OUTPUT
-----------------------------------------------
Return SUCCESS when:
• All news files are fetched
• The final file all_news_summaries.json is created
    """,

    expected_output="""
SUCCESS: 
✓ News fetched for all stocks  
✓ ALL summaries merged into data/all_news_summaries.json
    """,

    agent=news_agent,
    async_execution=False
)
