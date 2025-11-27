import os
import json
import time
from datetime import datetime

# CrewAI imports
from crewai import Crew, Process

# Agents
from agents.toolchain_agent import toolchain_agent
from agents.json_cleaner_agent import json_cleaner_agent
from agents.news_agent import news_agent

# Tasks
from tasks.toolchain_task import toolchain_task
from tasks.json_cleaner_task import json_cleaner_task
from tasks.news_task import news_task

# Discord notifier
from tools.notifier import DiscordNotifierTool

# -------------------------
# CLEANUP FUNCTION
# -------------------------
def cleanup_all_pipeline_files():
    """Delete all JSON pipeline files after run."""
    BASE = "data"
    NEWS_DIR = os.path.join(BASE, "news")

    general_files = [
        "classified_stocks.json",
        "clean_classified_stocks.json",
        "new_classified_stocks.json",
        "stock_analysis.json",
        "top_gainers.json"
    ]

    print("\n🧹 Cleaning pipeline files...")

    # delete general files
    for file in general_files:
        path = os.path.join(BASE, file)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"🗑️ Deleted: {path}")
            except:
                print(f"⚠️ Could not delete: {path}")

    # delete news files
    if os.path.exists(NEWS_DIR):
        for f in os.listdir(NEWS_DIR):
            if f.endswith("_news.json"):
                try:
                    os.remove(os.path.join(NEWS_DIR, f))
                    print(f"🗑️ Deleted: {f}")
                except:
                    print(f"⚠️ Could not delete: {f}")

    print("🧹 Cleanup complete.\n")


# -------------------------
# RUN FULL PIPELINE
# -------------------------
def run_pipeline():
    print("\n" + "="*70)
    print(f"🚀 Pipeline started at {datetime.now()}")
    print("="*70)

    # 1️⃣ TOOLCHAIN
    print("\n📊 Step 1: Running Toolchain...")
    crew1 = Crew(
        agents=[toolchain_agent],
        tasks=[toolchain_task],
        verbose=True,
        process=Process.sequential
    )
    crew1.kickoff()
    print("✔ Toolchain completed")

    # 2️⃣ CLEAN JSON
    print("\n🧹 Step 2: Cleaning JSON...")
    crew2 = Crew(
        agents=[json_cleaner_agent],
        tasks=[json_cleaner_task],
        verbose=True,
        process=Process.sequential
    )
    crew2.kickoff()
    print("✔ JSON cleaned")

    # 3️⃣ FETCH + PROCESS NEWS
    print("\n📰 Step 3: Fetching + Injecting News...")
    crew3 = Crew(
        agents=[news_agent],
        tasks=[news_task],
        verbose=True,
        process=Process.sequential
    )
    crew3.kickoff()
    print("✔ News processed")

    # 4️⃣ SEND TO DISCORD
    print("\n📨 Step 4: Sending to Discord...")
    notifier = DiscordNotifierTool()
    notifier._run()
    print("✔ Discord notification sent")

    # 5️⃣ CLEANUP FILES
    print("\n🧹 Step 5: Cleanup...")
    cleanup_all_pipeline_files()

    print("\n" + "="*70)
    print("🎉 Pipeline FINISHED SUCCESSFULLY.")
    print("="*70)


if __name__ == "__main__":
    run_pipeline()
