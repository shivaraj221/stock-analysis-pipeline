import os
import json
from datetime import datetime
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
# DATA VERIFICATION FUNCTION
# -------------------------
def verify_data_exists():
    """Check if we have valid data before sending to Discord"""
    clean_file = "data/clean_classified_stocks.json"
    
    if not os.path.exists(clean_file):
        print("❌ clean_classified_stocks.json does not exist")
        return False
    
    try:
        with open(clean_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check data structure
        stocks = []
        if isinstance(data, list):
            stocks = data
        elif isinstance(data, dict) and 'stocks' in data:
            stocks = data['stocks']
        else:
            print(f"❌ Unexpected data format: {type(data)}")
            return False
        
        if not stocks:
            print("❌ No stocks found in the data")
            return False
        
        print(f"✅ Data verified: {len(stocks)} stocks found")
        return True
        
    except Exception as e:
        print(f"❌ Error reading clean_classified_stocks.json: {e}")
        return False


# -------------------------
# RUN FULL PIPELINE
# -------------------------
def run_pipeline():
    print("\n" + "="*70)
    print(f"🚀 Pipeline started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    try:
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

        # ✅ VERIFY DATA BEFORE DISCORD
        print("\n🔍 Verifying data...")
        if not verify_data_exists():
            raise Exception("Data verification failed - no valid stocks found")

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
        return True

    except Exception as e:
        print(f"\n❌ Pipeline FAILED: {e}")
        print("💡 Keeping files for debugging...")
        return False


if __name__ == "__main__":
    # Simple one-time execution for GitHub Actions
    success = run_pipeline()
    exit(0 if success else 1)
