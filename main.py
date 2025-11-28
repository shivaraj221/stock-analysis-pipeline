import os
import schedule
import time
from datetime import datetime
from crewai import Crew, Process
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import agents
from agents.toolchain_agent import toolchain_agent
from agents.json_cleaner_agent import json_cleaner_agent
from agents.news_agent import news_agent

# Import tasks
from tasks.toolchain_task import toolchain_task
from tasks.json_cleaner_task import json_cleaner_task
from tasks.news_task import news_task

# Import notifier
from tools.notifier import DiscordNotifierTool


# -----------------------------------------------------------
# RUN COMPLETE CREW PIPELINE (Stock → Clean → News)
# -----------------------------------------------------------
def run_crewai_pipeline():
    print("\n🚀 Running CrewAI Stock Pipeline...")

    full_crew = Crew(
        agents=[
            toolchain_agent,
            json_cleaner_agent,
            news_agent
        ],
        tasks=[
            toolchain_task,
            json_cleaner_task,
            news_task
        ],
        process=Process.sequential,
        verbose=False
    )

    result = full_crew.kickoff()

    print("✅ Crew pipeline finished.")
    return result


# -----------------------------------------------------------
# SINGLE EXECUTION WITH TIME CHECK
# -----------------------------------------------------------
def run_once():
    now = datetime.now()
    hour = now.hour

    # Only run between 12 PM → 6 PM
    if 12 <= hour <= 18:
        print(f"\n⏱️ Executing scheduled run at {now.strftime('%I:%M %p')}")

        final_output = run_crewai_pipeline()

        # Send Discord notification
        notifier = DiscordNotifierTool()
        notifier.run(final_output)

        print("📨 Notification sent successfully!")
    else:
        print(f"⏳ Outside allowed window ({now.strftime('%I:%M %p')}) — skipping.")


# -----------------------------------------------------------
# MAIN SCHEDULER LOOP
# -----------------------------------------------------------
def main():
    print("⏳ Scheduler started — Will run every hour between 12 PM and 6 PM.")

    # Run immediately on startup
    print("🚀 Running initial pipeline now...")
    run_once()

    # Schedule hourly
    schedule.every().hour.do(run_once)

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check once per minute


# -----------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------
if __name__ == "__main__":
    main()
