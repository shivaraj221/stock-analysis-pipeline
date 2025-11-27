import os
import json
import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class NewsFetcherInput(BaseModel):
    """Input schema for NewsFetcherTool - no arguments needed"""
    dummy_field: str = Field(default="", description="No arguments needed for this tool")

class NewsFetcherTool(BaseTool):
    name: str = "News Fetcher Tool"
    description: str = (
        "Fetches the latest news articles for all stocks listed in clean_classified_stocks.json using NewsAPI. "
        "Saves each stock's news to data/news/{symbol}_news.json. "
        "Call this tool without any arguments to start the full fetch process."
    )
    args_schema: Type[BaseModel] = NewsFetcherInput

    def _run(self, dummy_field: str = "") -> str:
        """Main execution method"""
        API_KEY = "ac8e859ef070410396186e07e2981682"

        def get_stock_news(symbol: str):
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": symbol,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 10,
                "apiKey": API_KEY
            }
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                return data.get("articles", [])[:10]
            except Exception as e:
                print(f"   Failed to fetch news for {symbol}: {e}")
                return []

        # Read from clean_classified_stocks.json instead of top_gainers.json
        CLEAN_FILE = r"C:\Users\Admin\Desktop\crewai-1\crewai\data\clean_classified_stocks.json"
        DATA_OUTPUT_FOLDER = r"C:\Users\Admin\Desktop\crewai-1\crewai\data\news"

        os.makedirs(DATA_OUTPUT_FOLDER, exist_ok=True)

        if not os.path.exists(CLEAN_FILE):
            return f"Error: Clean classified stocks file not found: {CLEAN_FILE}"

        try:
            with open(CLEAN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Extract stocks from different possible structures
            if isinstance(data, list):
                stocks = data
            elif isinstance(data, dict) and "stocks" in data:
                stocks = data["stocks"]
            elif isinstance(data, dict):
                stocks = [data]
            else:
                return "Error: Unsupported data structure in clean_classified_stocks.json"
                
        except Exception as e:
            return f"Error reading clean_classified_stocks.json: {e}"

        if not stocks:
            return "Error: No valid stock data in clean_classified_stocks.json"

        print(f"Found {len(stocks)} stocks in clean_classified_stocks.json. Starting news fetch...")

        success = 0
        for stock in stocks:
            symbol = stock.get("symbol")
            if not symbol:
                continue

            print(f"   Fetching news for {symbol}...")
            articles = get_stock_news(symbol)

            output_file = os.path.join(DATA_OUTPUT_FOLDER, f"{symbol}_news.json")
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(articles, f, ensure_ascii=False, indent=4)
                count = len(articles)
                sample = articles[0].get("title", "No title")[:70] + "..." if articles else "No articles"
                print(f"   Saved {count} articles → {sample}")
                success += 1
            except Exception as e:
                print(f"   Failed to save {symbol}: {e}")

        return f"News fetching completed: {success}/{len(stocks)} stocks saved to {DATA_OUTPUT_FOLDER}"