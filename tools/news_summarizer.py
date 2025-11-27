import os
import json
import logging
from datetime import datetime
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsSummarizerInput(BaseModel):
    """Input schema for NewsSummarizerTool"""
    dummy_field: str = Field(default="", description="No arguments needed for this tool")

class NewsSummarizerTool(BaseTool):
    name: str = "News Summarizer Tool"
    description: str = "Loads news from data/news folder, summarizes all articles and adds summary attribute to clean_classified_stocks.json"
    args_schema: Type[BaseModel] = NewsSummarizerInput

    def _run(self, dummy_field: str = "") -> str:
        """Process all news articles and add summary attribute to clean_classified_stocks.json"""
        try:
            BASE_DIR = r"C:\Users\Admin\Desktop\crewai-1\crewai"
            NEWS_DIR = os.path.join(BASE_DIR, "data", "news")
            CLEAN_FILE = os.path.join(BASE_DIR, "data", "clean_classified_stocks.json")
            
            logger.info(f"📁 News directory: {NEWS_DIR}")
            logger.info(f"💾 Clean file: {CLEAN_FILE}")

            # Validate paths
            if not os.path.exists(NEWS_DIR):
                error_msg = f"❌ News directory not found: {NEWS_DIR}"
                logger.error(error_msg)
                return error_msg

            if not os.path.exists(CLEAN_FILE):
                error_msg = f"❌ Clean classified stocks file not found: {CLEAN_FILE}"
                logger.error(error_msg)
                return error_msg

            # Load clean_classified_stocks.json
            logger.info("📖 Reading clean_classified_stocks.json...")
            try:
                with open(CLEAN_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                logger.info("✅ Successfully loaded clean_classified_stocks.json")
            except Exception as e:
                error_msg = f"❌ Error reading clean_classified_stocks.json: {str(e)}"
                logger.error(error_msg)
                return error_msg

            # Handle different data structures
            if isinstance(data, list):
                stocks = data
                original_structure = "list"
                logger.info("📊 Data format: List of stocks")
            elif isinstance(data, dict) and "stocks" in data:
                stocks = data["stocks"]
                original_structure = "dict_with_stocks"
                logger.info("📊 Data format: Dict with 'stocks' key")
            elif isinstance(data, dict):
                stocks = [data]
                original_structure = "single_dict"
                logger.info("📊 Data format: Single stock dict -> Converting to list")
            else:
                error_msg = f"❌ Unexpected data format in clean_classified_stocks.json: {type(data)}"
                logger.error(error_msg)
                return error_msg

            if not stocks:
                error_msg = "❌ No stocks found in clean_classified_stocks.json"
                logger.error(error_msg)
                return error_msg

            logger.info(f"📈 Found {len(stocks)} stocks to process")

            # List all news files
            news_files = [f for f in os.listdir(NEWS_DIR) if f.endswith('_news.json')]
            logger.info(f"📰 Found {len(news_files)} news files: {news_files}")

            processed = 0
            no_news_count = 0
            error_count = 0

            # Create a mapping of symbol to news data
            news_data_map = {}
            for news_file in news_files:
                symbol = news_file.replace('_news.json', '')
                news_file_path = os.path.join(NEWS_DIR, news_file)
                
                try:
                    with open(news_file_path, "r", encoding="utf-8") as f:
                        articles = json.load(f)
                    news_data_map[symbol] = articles
                except Exception as e:
                    logger.error(f"❌ Error loading news for {symbol}: {e}")
                    news_data_map[symbol] = []

            # Process each stock and add summary
            for stock in stocks:
                symbol = stock.get("symbol")
                if not symbol:
                    logger.warning("⚠️ Skipping stock with no symbol")
                    continue

                logger.info(f"🔍 Processing news for {symbol}...")

                if symbol not in news_data_map:
                    logger.warning(f"⚠️ No news file found for {symbol}")
                    stock["summary"] = "No recent news articles found for this stock."
                    no_news_count += 1
                    continue

                articles = news_data_map[symbol]

                if not articles or not isinstance(articles, list):
                    logger.warning(f"   ⚠️ No valid articles for {symbol}")
                    stock["summary"] = "No valid news articles found."
                    no_news_count += 1
                    continue

                # Build summary from articles
                try:
                    summary_parts = []
                    valid_articles = 0
                    
                    for i, article in enumerate(articles[:5]):  # Limit to 5 articles
                        title = article.get("title", "").strip()
                        description = article.get("description", "").strip()
                        source = article.get("source", {})
                        source_name = source.get("name", "Unknown") if isinstance(source, dict) else str(source)
                        published_at = article.get("publishedAt", "")

                        # Skip articles with no title
                        if not title or len(title) < 10:
                            continue

                        # Build article entry
                        article_entry = f"• {title}"
                        if description and description != title:
                            if len(description) > 100:
                                description = description[:100] + "..."
                            article_entry += f" - {description}"
                        
                        if source_name and source_name != "Unknown":
                            article_entry += f" ({source_name})"
                        
                        if published_at:
                            date_part = published_at.split('T')[0]
                            article_entry += f" - {date_part}"

                        summary_parts.append(article_entry)
                        valid_articles += 1

                    if summary_parts:
                        # Create final summary
                        stock["summary"] = f"Recent news for {symbol}:\n" + "\n".join(summary_parts)
                        processed += 1
                        logger.info(f"   ✅ Added summary with {valid_articles} articles for {symbol}")
                    else:
                        stock["summary"] = "No relevant news articles with valid content found."
                        no_news_count += 1
                        logger.info(f"   ⚠️ No valid content for {symbol}")

                except Exception as e:
                    error_msg = f"   ❌ Error processing news for {symbol}: {e}"
                    logger.error(error_msg)
                    stock["summary"] = f"Error processing news data: {str(e)}"
                    error_count += 1

            # Save the updated data back to clean_classified_stocks.json
            logger.info("💾 Saving updated data to clean_classified_stocks.json...")
            try:
                # Reconstruct the original structure
                if original_structure == "list":
                    save_data = stocks
                elif original_structure == "dict_with_stocks":
                    data["stocks"] = stocks
                    save_data = data
                else:  # single_dict
                    save_data = stocks[0] if stocks else {}

                with open(CLEAN_FILE, "w", encoding="utf-8") as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False, default=str)
                
                logger.info("✅ Successfully saved clean_classified_stocks.json with summary attributes")

            except Exception as e:
                error_msg = f"❌ Error saving clean_classified_stocks.json: {e}"
                logger.error(error_msg)
                return error_msg

            # Generate final report
            result_lines = [
                "\n" + "="*60,
                "📊 NEWS SUMMARIZER - EXECUTION REPORT",
                "="*60,
                f"✅ Successfully processed: {processed} stocks",
                f"⚠️  No news found: {no_news_count} stocks", 
                f"❌ Errors encountered: {error_count} stocks",
                f"📁 Total stocks in file: {len(stocks)}",
                f"💾 Updated file: {CLEAN_FILE}",
                f"📰 New attribute: 'summary' added to each stock",
                "="*60
            ]
            
            result = "\n".join(result_lines)
            logger.info(result)
            return result

        except Exception as e:
            error_msg = f"❌ Unexpected error in NewsSummarizerTool: {str(e)}"
            logger.error(error_msg)
            return error_msg

# Test function
def test_summarizer():
    """Test the news summarizer tool"""
    print("🧪 Testing News Summarizer Tool...")
    tool = NewsSummarizerTool()
    result = tool._run()
    print(result)

if __name__ == "__main__":
    test_summarizer()