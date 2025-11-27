import json
import os
import requests
from crewai.tools import BaseTool

DATA_FOLDER = r"C:\Users\Admin\Desktop\crewai-1\crewai\data"
os.makedirs(DATA_FOLDER, exist_ok=True)
OUTPUT_FILE = os.path.join(DATA_FOLDER, "top_gainers.json")


class YahooAPIClient:
    API_URL = (
        "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"
        "?scrIds=day_gainers&count=5"
    )

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    def fetch(self, limit=5):
        try:
            response = requests.get(self.API_URL, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            quotes = data["finance"]["result"][0]["quotes"]
            results = []

            for q in quotes[:limit]:
                results.append({
                    "symbol": q.get("symbol"),
                    "price": q.get("regularMarketPrice", 0),
                    "change_percent": q.get("regularMarketChangePercent", 0),
                    "volume": q.get("regularMarketVolume", 0)
                })

            return results

        except Exception as e:
            print("Yahoo API error:", e)
            return []


class TrendingStocksTool(BaseTool):
    name: str = "trending_stocks_tool"
    description: str = "FAST & RELIABLE Yahoo gainers fetcher (API-based)."

    def _run(self, limit: int = 5) -> str:
        client = YahooAPIClient()
        data = client.fetch(limit=limit)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        return f"Fetched {len(data)} gainers → {OUTPUT_FILE}"


if __name__ == "__main__":
    tool = TrendingStocksTool()
    print(tool.run())
