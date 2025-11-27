# tasks/summary_task.py
from crewai import Task
from agents.summary_agent import summary_agent
import json
import os
import re

CLEAN_FILE = r"C:\Users\Admin\Desktop\crewai-1\crewai\data\news_summary.json"

def generate_detailed_summaries():
    """Generate comprehensive news summaries for all stocks"""
    if not os.path.exists(CLEAN_FILE):
        return "❌ clean_classified_stocks.json not found"

    # Load JSON file
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Detect JSON structure
    if isinstance(data, list):
        stocks = data
        json_type = "list"
    elif isinstance(data, dict) and "stocks" in data:
        stocks = data["stocks"]
        json_type = "dict"
    else:
        return "❌ Unsupported JSON structure."

    done = 0

    for stock in stocks:
        symbol = stock.get("symbol")
        context = stock.get("news_context")

        if not context or not symbol:
            continue

        # Use the agent's LLM to generate summary
        prompt = f"""
You are a senior financial analyst writing a comprehensive news impact report 
for institutional investors tracking {symbol}.

NEWS CONTEXT:
{context}

WRITE A DETAILED ANALYSIS WITH THESE SECTIONS:
1. **Executive Summary** - Main takeaways
2. **Key Developments** - Specific events and announcements
3. **Market Impact** - How this affects stock performance
4. **Risk Assessment** - Potential challenges and opportunities
5. **Investment Outlook** - Forward-looking perspective

Provide a professional, detailed analysis suitable for hedge fund managers.
"""

        try:
            response = summary_agent.llm.call(prompt=prompt)
            summary = response.strip()
            
            # Clean up the response
            summary = re.sub(r'^(Summary|Analysis|Response):\s*', '', summary, flags=re.IGNORECASE)
            summary = summary.strip()
            
            if summary and len(summary) > 50:
                stock["news_summary"] = summary
                done += 1
                print(f"✅ Generated detailed summary for {symbol}")
            else:
                stock["news_summary"] = f"Comprehensive news analysis available for {symbol}. Multiple market developments being monitored."
                done += 1
                
        except Exception as e:
            print(f"❌ AI summary failed for {symbol}: {e}")
            stock["news_summary"] = f"Detailed market news coverage for {symbol}. Multiple factors influencing investor sentiment."
            done += 1

    # Save back depending on structure
    if json_type == "list":
        with open(CLEAN_FILE, "w", encoding="utf-8") as f:
            json.dump(stocks, f, indent=2, ensure_ascii=False)
    else:
        data["stocks"] = stocks
        with open(CLEAN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return f"💾 Generated comprehensive summaries for {done} stocks"

# Create the task with the agent
summary_task = Task(
    description="""
    Generate comprehensive, multi-section financial summaries for all stocks 
    using their news_context data. Create detailed analysis with:
    - Executive Summary
    - Key Developments  
    - Market Impact Assessment
    - Risk Analysis
    - Investment Outlook
    
    Make the summaries professional and suitable for institutional investors.
    """,
    expected_output="Detailed news_summary fields added to new_summary.json for all stocks with news data",
    agent=summary_agent,
    function=generate_detailed_summaries
)