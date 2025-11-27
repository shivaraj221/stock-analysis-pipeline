import json
import yfinance as yf
import numpy as np
import pandas as pd
import os

from typing import Dict, Any, Optional, List
from crewai.tools import BaseTool


# ----------------------------------------------------
# Helper
# ----------------------------------------------------
def safe(info, key, default=None):
    v = info.get(key, default)
    return v if v not in [None, "", "None"] else default


# ----------------------------------------------------
# Core Analyzer
# ----------------------------------------------------
class StockAnalyzer:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)

    def load_data(self):
        try:
            data = self.ticker.history(period="1y")
            info = self.ticker.info
            if data is None or data.empty:
                return None, None
            return data, info
        except:
            return None, None

    def analyze(self) -> Optional[Dict[str, Any]]:
        data, info = self.load_data()
        if data is None:
            print(f"❌ {self.symbol}: NO DATA")
            return None

        today = data.iloc[-1]
        close = data["Close"]
        high = data["High"]
        low = data["Low"]
        volume = data["Volume"]
        close_today = today["Close"]

        # ----------------------------- PRICE ACTION
        price_change = float(((today["Close"] - today["Open"]) / today["Open"]) * 100)
        one_year_return = float(((close_today - data.iloc[0]["Close"]) / data.iloc[0]["Close"]) * 100)
        vol_daily = close.pct_change().dropna()
        annual_vol = float(vol_daily.std() * np.sqrt(252) * 100)

        try:
            tr = np.maximum(high - low, np.maximum(abs(high - close.shift()), abs(low - close.shift())))
            atr = float(tr.rolling(14).mean().iloc[-1])
        except:
            atr = None

        try:
            sharpe = float((vol_daily.mean() / vol_daily.std()) * np.sqrt(252))
        except:
            sharpe = None

        try:
            downside = vol_daily[vol_daily < 0]
            sortino = float((vol_daily.mean() / downside.std()) * np.sqrt(252)) if not downside.empty else None
        except:
            sortino = None

        # ----------------------------- TRENDS
        MA20 = float(close.tail(20).mean())
        MA50 = float(close.tail(50).mean())
        MA200 = float(close.tail(200).mean())
        golden_cross = 1 if MA50 > MA200 else 0

        # RSI
        try:
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rsi = 100 - (100 / (1 + gain / loss))
            rsi_t = float(rsi.iloc[-1])
        except:
            rsi_t = None

        # MACD
        try:
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            macd_series = ema12 - ema26
            signal_series = macd_series.ewm(span=9).mean()
            macd_t = float(macd_series.iloc[-1])
            signal_t = float(signal_series.iloc[-1])
        except:
            macd_t, signal_t = None, None

        # Stochastic
        try:
            lowest_low = low.rolling(14).min()
            highest_high = high.rolling(14).max()
            stochastic = ((close - lowest_low) / (highest_high - lowest_low)) * 100
            stochastic_t = float(stochastic.iloc[-1])
        except:
            stochastic_t = None

        # ----------------------------- VOLUME
        vol_ma = float(volume.tail(20).mean())
        try:
            volume_spike = float(((today["Volume"] - vol_ma) / vol_ma) * 100)
        except:
            volume_spike = None

        try:
            obv = float((np.sign(close.diff()) * volume).fillna(0).cumsum().iloc[-1])
        except:
            obv = None

        # ----------------------------- FUNDAMENTALS
        pe = safe(info, "trailingPE")
        ps = safe(info, "priceToSalesTrailing12Months")
        pb = safe(info, "priceToBook")
        peg = safe(info, "pegRatio")
        ev_ebitda = safe(info, "enterpriseToEbitda")

        rev_g = (safe(info, "revenueGrowth", 0) or 0) * 100
        eps_g = (safe(info, "earningsQuarterlyGrowth", 0) or 0) * 100

        pm = (safe(info, "profitMargins", 0) or 0) * 100
        gm = (safe(info, "grossMargins", 0) or 0) * 100
        opm = (safe(info, "operatingMargins", 0) or 0) * 100
        roe = safe(info, "returnOnEquity")
        roa = safe(info, "returnOnAssets")

        beta = safe(info, "beta")
        f2l = safe(info, "fiftyTwoWeekLow")
        d_low = ((close_today / f2l) - 1) * 100 if f2l else None

        debt_e = safe(info, "debtToEquity")
        curr_ratio = safe(info, "currentRatio")
        quick_ratio = safe(info, "quickRatio")

        total_cash = safe(info, "totalCash", 0)
        total_debt = safe(info, "totalDebt", 0)
        cash_debt = (total_cash / total_debt) if total_debt not in [0, None] else None

        analyst_rec = safe(info, "recommendationMean")
        target_price = safe(info, "targetMeanPrice")
        target_upside = ((target_price - close_today) / close_today * 100) if target_price else None

        return {
            "symbol": self.symbol,
            "price_change": price_change,
            "one_year_return": one_year_return,
            "annual_vol": annual_vol,
            "ATR": atr,
            "sharpe": sharpe,
            "sortino": sortino,
            "MA20": MA20,
            "MA50": MA50,
            "MA200": MA200,
            "golden_cross": golden_cross,
            "rsi": rsi_t,
            "macd": macd_t,
            "signal": signal_t,
            "stochastic": stochastic_t,
            "volume_spike": volume_spike,
            "vol_ma": vol_ma,
            "OBV": obv,
            "pe": pe,
            "ps": ps,
            "pb": pb,
            "peg": peg,
            "ev_ebitda": ev_ebitda,
            "rev_g": rev_g,
            "eps_g": eps_g,
            "pm": pm,
            "gm": gm,
            "opm": opm,
            "roe": roe,
            "roa": roa,
            "beta": beta,
            "d_low": d_low,
            "debt_e": debt_e,
            "current_ratio": curr_ratio,
            "quick_ratio": quick_ratio,
            "cash_to_debt": cash_debt,
            "analyst_rec": analyst_rec,
            "target_upside": target_upside
        }


# ----------------------------------------------------
# CrewAI Tool Conversion
# ----------------------------------------------------
class YFinanceAnalysisTool(BaseTool):
    name: str = "yfinance_analysis_tool"
    description: str = (
        "Fetches technical + fundamental metrics for each stock in top_gainers.json "
        "and writes output to stock_analysis.json"
    )

    def _run(self) -> str:
        input_file = r"C:\Users\Admin\Desktop\crewai-1\crewai\data\top_gainers.json"  # Changed to .txt
        output_file = r"C:\Users\Admin\Desktop\crewai-1\crewai\data\stock_analysis.json"  # Changed to .txt

        # Load from TXT file
        with open(input_file, "r", encoding="utf-8") as f:
            stocks = json.loads(f.read())

        final_results = []

        for s in stocks:
            symbol = s["symbol"]
            print(f"📌 Analyzing: {symbol}")
            analyzer = StockAnalyzer(symbol)

            result = analyzer.analyze()
            if result:
                final_results.append(result)

        # Save as JSON string in TXT file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(final_results, indent=4, ensure_ascii=False))

        return f"✅ Analysis completed. Saved to: {output_file}"


# ----------------------------------------------------
# Standalone script mode
# ----------------------------------------------------
if __name__ == "__main__":
    tool = YFinanceAnalysisTool()
    print(tool.run())