# main.py
import os
import json
from crewai import Crew, Process
from dotenv import load_dotenv

load_dotenv()

# Agents
from agents.toolchain_agent import toolchain_agent
from agents.json_cleaner_agent import json_cleaner_agent
from agents.news_agent import news_agent
from agents.notifier_agent import notifier_agent

# Tasks
from tasks.toolchain_task import toolchain_task
from tasks.json_cleaner_task import json_cleaner_task
from tasks.news_task import news_task
from tasks.notifier_task import notify_task

DATA_DIR = "data"
NEWS_DIR = "data/news"

def cleanup_files():
    print("\n🧹 Cleaning old JSON files...")

    to_delete = [
        "classified_stocks.json",
        "clean_classified_stocks.json",
        "new_classified_stocks.json",
        "stock_analysis.json",
        "top_gainers.json"
    ]

    # Delete pipeline JSON files
    for file in to_delete:
        path = os.path.join(DATA_DIR, file)
        if os.path.exists(path):
            os.remove(path)
            print("🗑️ Deleted:", file)

    # Delete all news files
    if os.path.exists(NEWS_DIR):
        for f in os.listdir(NEWS_DIR):
            if f.endswith("_news.json"):
                os.remove(os.path.join(NEWS_DIR, f))
                print("🗑️ Deleted:", f)

    print("🧹 Cleanup complete.\n")


def run_pipeline_once():
    print("\n🚀 RUNNING FULL PIPELINE...\n")

    Crew(
        agents=[toolchain_agent],
        tasks=[toolchain_task],
        process=Process.sequential
    ).kickoff()

    Crew(
        agents=[json_cleaner_agent],
        tasks=[json_cleaner_task],
        process=Process.sequential
    ).kickoff()

    Crew(
        agents=[news_agent],
        tasks=[news_task],
        process=Process.sequential
    ).kickoff()

    Crew(
        agents=[notifier_agent],
        tasks=[notify_task],
        process=Process.sequential
    ).kickoff()

    print("\n🎉 Pipeline completed successfully!\n")


if __name__ == "__main__":
    cleanup_files()       # Remove old files
    run_pipeline_once()   # Run everything once
    cleanup_files()       # Clean again after sending
