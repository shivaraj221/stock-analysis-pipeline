# import os
# import sys
# from crewai import Crew, Process
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Import agents
# from agents.json_cleaner_agent import json_cleaner_agent
# from agents.news_agent import news_agent
# from agents.notifier_agent import notifier_agent
# from agents.toolchain_agent import toolchain_agent

# # Import tasks
# from tasks.json_cleaner_task import json_cleaner_task
# from tasks.news_task import news_task
# from tasks.notifier_task import notify_task
# from tasks.toolchain_task import toolchain_task

# def main():
#     """Main execution function for the AI Stock Analysis Pipeline"""
    
#     print("🚀 Starting AI Stock Analysis Pipeline...")
    
#     try:
#         # Create the main crew with SILENT mode
#         stock_analysis_crew = Crew(
#             agents=[
#                 toolchain_agent,
#                 json_cleaner_agent, 
#                 news_agent,
#                 notifier_agent
#             ],
#             tasks=[
#                 toolchain_task,
#                 json_cleaner_task,
#                 news_task,
#                 notify_task
#             ],
#             verbose=False,  # ⚡ TURN OFF VERBOSE LOGGING
#             process=Process.sequential
#         )
        
#         # Execute silently
#         result = stock_analysis_crew.kickoff()
        
#         print(f"✅ Pipeline completed: {result}")
        
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         return 1
    
#     return 0

# if __name__ == "__main__":
#     result = main()
#     sys.exit(result)
import os
import time
import schedule
import json
from datetime import datetime
from dotenv import load_dotenv

from crewai import Crew, Process

# Load environment variables
load_dotenv()

# Agents
from agents.toolchain_agent import toolchain_agent
from agents.json_cleaner_agent import json_cleaner_agent
from agents.news_agent import news_agent

# Tasks
from tasks.toolchain_task import toolchain_task
from tasks.json_cleaner_task import json_cleaner_task
from tasks.news_task import news_task

# Discord Notifier
from tools.notifier import DiscordNotifierTool


# ============================================================
#  CLEANUP FUNCTION – Deletes all pipeline JSON files
# ============================================================
def cleanup_pipeline_files():
    """Deletes ALL intermediate and news JSON files after each run."""
    BASE = r"C:\Users\Admin\Desktop\crewai-1\crewai\data"
    NEWS_DIR = os.path.join(BASE, "news")

    # List of general files to delete
    general_files = [
        "classified_stocks.json",
        "clean_classified_stocks.json",
        "new_classified_stocks.json",
        "stock_analysis.json",
        "top_gainers.json",
    ]

    print("\n🧹 Starting cleanup...")

    # Delete general files
    deleted_count = 0
    for filename in general_files:
        path = os.path.join(BASE, filename)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"🗑️ Deleted: {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ Could not delete {filename}: {e}")

    # Delete all news/*.json files
    if os.path.exists(NEWS_DIR):
        for f in os.listdir(NEWS_DIR):
            if f.endswith("_news.json"):
                try:
                    os.remove(os.path.join(NEWS_DIR, f))
                    print(f"🗑️ Deleted news file: {f}")
                    deleted_count += 1
                except Exception as e:
                    print(f"⚠️ Could not delete news file {f}: {e}")

    print(f"🧹 Cleanup complete. {deleted_count} files deleted.\n")
    return deleted_count


# ============================================================
#  VERIFY DATA FUNCTION - Check if we have valid data
# ============================================================
def verify_data_exists():
    """Check if clean_classified_stocks.json exists and has valid data"""
    clean_file = r"C:\Users\Admin\Desktop\crewai-1\crewai\data\clean_classified_stocks.json"
    
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
        
        # Show first few stocks for debugging
        for i, stock in enumerate(stocks[:3]):
            symbol = stock.get('symbol', 'Unknown')
            action = stock.get('action', stock.get('recommendation', 'No action'))
            print(f"   {i+1}. {symbol}: {action}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading clean_classified_stocks.json: {e}")
        return False


# ============================================================
#  RUN FULL PIPELINE WITHOUT CLEANUP AT START
# ============================================================
def run_crewai_pipeline():
    """Runs all pipeline tasks sequentially and returns final output."""
    print("\n🚀 Running CrewAI Full Pipeline...")

    # 🚫 NO CLEANUP HERE - We handle cleanup AFTER Discord in run_once()

    # 1️⃣ Toolchain (Scrape → Analyze → Classify)
    print("\n📈 STEP 1: Running Toolchain...")
    toolchain_crew = Crew(
        agents=[toolchain_agent],
        tasks=[toolchain_task],
        verbose=False,  # Reduced verbosity
        process=Process.sequential
    )
    toolchain_result = toolchain_crew.kickoff()
    print("✅ Toolchain completed")

    # 2️⃣ Clean messy JSON
    print("\n🧹 STEP 2: Cleaning JSON...")
    cleaner_crew = Crew(
        agents=[json_cleaner_agent],
        tasks=[json_cleaner_task],
        verbose=False,
        process=Process.sequential
    )
    cleaner_result = cleaner_crew.kickoff()
    print("✅ JSON cleaning completed")

    # 3️⃣ Fetch news + build news_context
    print("\n📰 STEP 3: Processing News...")
    news_crew = Crew(
        agents=[news_agent],
        tasks=[news_task],
        verbose=False,
        process=Process.sequential
    )
    news_result = news_crew.kickoff()
    print("✅ News processing completed")

    # Verify we have data before continuing
    if not verify_data_exists():
        raise Exception("Pipeline failed - no valid data produced")

    return "SUCCESS: Pipeline completed with valid data"


# ============================================================
#  TIME CHECK FUNCTION
# ============================================================
def should_run_now():
    """Check if current time is between 7:00 PM and 7:20 PM"""
    now = datetime.now()
    current_time = now.time()
    
    # Define time range (7:00 PM to 7:20 PM)
    start_time = datetime.strptime("20:00", "%H:%M").time()
    end_time = datetime.strptime("1:30", "%H:%M").time()
    
    return start_time <= current_time <= end_time


# ============================================================
#  RUN ONCE (PROPER ORDER: PIPELINE → DISCORD → CLEANUP)
# ============================================================
def run_once():
    now = datetime.now()
    current_time = now.strftime('%I:%M %p')

    if should_run_now():
        print(f"\n" + "="*60)
        print(f"⏰ EXECUTION STARTED AT: {current_time}")
        print("="*60)

        try:
            # 🚀 Run full pipeline (creates fresh JSON files)
            pipeline_result = run_crewai_pipeline()
            
            # 📨 Send to Discord (uses the fresh data)
            print("\n📨 Sending to Discord...")
            notifier = DiscordNotifierTool()
            notifier_result = notifier._run()  # Use _run() method
            print("✅ Discord notification sent successfully!")

            # 🧹 DELETE ALL JSON FILES AFTER DISCORD
            print("\n🧹 Cleaning up files after Discord notification...")
            deleted_count = cleanup_pipeline_files()
            print(f"✅ Cleaned up {deleted_count} files - Ready for next fresh cycle")

            print(f"\n🎯 EXECUTION COMPLETED AT: {datetime.now().strftime('%I:%M %p')}")
            print(f"📊 Result: {pipeline_result}")
            print("="*60 + "\n")

        except Exception as e:
            print(f"❌ Execution failed: {e}")
            print("💡 Keeping files for debugging...")
            print("="*60 + "\n")
            
    else:
        print(f"⏳ Skipping. Current time {current_time} is outside 7:00 PM - 7:20 PM allowed hours.")


# ============================================================
#  SCHEDULED TASK WRAPPER
# ============================================================
def scheduled_task():
    """Wrapper function for scheduling - only runs during allowed time"""
    if should_run_now():
        run_once()
    else:
        now = datetime.now().strftime('%I:%M %p')
        print(f"⏳ Skipping - Current time {now} is outside 7:00 PM - 7:20 PM range")


# ============================================================
#  MAIN LOOP (RUN EVERY 5 MINUTES FROM 7:00 PM TO 7:20 PM)
# ============================================================
def main():
    print("\n" + "="*60)
    print("🚀 STOCK ANALYSIS SCHEDULER ACTIVATED")
    print("="*60)
    print("📅 Schedule: Every 5 minutes from 7:00 PM to 7:20 PM")
    print("⏰ Execution times: 7:00, 7:05, 7:10, 7:15, 7:20 PM")
    print("🔄 Flow: Pipeline → Discord → Cleanup → Wait 5min")
    print("="*60)
    
    # Schedule every 5 minutes
    schedule.every(55).minutes.do(scheduled_task)
    
    # Initial execution if within time range
    if should_run_now():
        print("🚀 Running initial execution...")
        run_once()
    else:
        current_time = datetime.now().strftime('%I:%M %p')
        print(f"⏳ Waiting for 7:00 PM - 7:20 PM window (Current: {current_time})")
    
    print("\n🔄 Entering scheduling loop...")
    print("Press Ctrl+C to stop the scheduler")
    
    # Main scheduling loop
    while True:
        try:
            schedule.run_pending()
            
            # Print status every minute when in active window
            current_time = datetime.now()
            if should_run_now():
                if current_time.minute % 1 == 0:  # Every minute during active window
                    print(f"🟢 Active - Current time: {current_time.strftime('%I:%M %p')} (Within 7:00-7:20 PM)")
            else:
                # Print status every 5 minutes when outside window
                if current_time.minute % 5 == 0:
                    print(f"🔴 Waiting - Current time: {current_time.strftime('%I:%M %p')}")
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Scheduler stopped by user")
            break
        except Exception as e:
            print(f"❌ Scheduler error: {e}")
            time.sleep(60)  # Wait 1 minute on error


# ============================================================
if __name__ == "__main__":
    main()