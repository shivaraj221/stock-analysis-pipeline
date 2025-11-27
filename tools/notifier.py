import json
import requests
import os
from datetime import datetime
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class DiscordNotifierInput(BaseModel):
    """Input schema for DiscordNotifierTool"""
    dummy_field: str = Field(default="", description="No arguments needed for this tool")

class DiscordNotifierTool(BaseTool):
    name: str = "Discord Notifier Tool"
    description: str = "Sends comprehensive stock analysis reports to Discord from clean_classified_stocks.json"
    args_schema: Type[BaseModel] = DiscordNotifierInput

    def _run(self, dummy_field: str = "") -> str:
        # HARDCODED WEBHOOK URL
        webhook_url = "https://discord.com/api/webhooks/1440999999109595248/i_revNiL_GzIj-CuYzLAkxDtWtSVoiWXdakk5H4uoue_ShbK1PXQ-kMa2HbRdAlMJAzc"
        
        print(f"🎯 DiscordNotifierTool starting with webhook...")
        
        json_path = r"C:\Users\Admin\Desktop\crewai-1\crewai\data\clean_classified_stocks.json"
        
        print(f"📁 Looking for file: {json_path}")

        # Check if file exists
        if not os.path.exists(json_path):
            error_msg = f"❌ ERROR: File not found at {json_path}"
            print(error_msg)
            return error_msg

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                stocks = data
                print(f"✅ Loaded {len(stocks)} stocks from list structure")
            elif isinstance(data, dict) and "stocks" in data:
                stocks = data["stocks"]
                print(f"✅ Loaded {len(stocks)} stocks from dict structure")
            elif isinstance(data, dict):
                stocks = [data]
                print(f"✅ Loaded single stock from dict structure")
            else:
                error_msg = f"❌ ERROR: Unexpected data type: {type(data)}"
                print(error_msg)
                return error_msg
                
        except Exception as e:
            error_msg = f"❌ ERROR reading JSON: {e}"
            print(error_msg)
            return error_msg

        # Validate that stocks is a list of dictionaries
        if not isinstance(stocks, list):
            error_msg = f"❌ ERROR: Expected list of stocks, got {type(stocks)}"
            print(error_msg)
            return error_msg

        # Send test message first
        print("🧪 Sending test message...")
        if not self._send(webhook_url, {"content": "🔔 **Comprehensive Stock Analysis Report Starting** - Sending detailed analysis..."}):
            error_msg = "❌ ERROR: Failed to send test message. Check webhook URL."
            print(error_msg)
            return error_msg

        # Send comprehensive summary
        print("📊 Sending comprehensive summary...")
        self._send_comprehensive_summary(webhook_url, stocks)
        
        # Send detailed analysis for each stock
        successful_stocks = 0
        for i, stock in enumerate(stocks, 1):
            if not isinstance(stock, dict):
                print(f"⚠️ Skipping non-dictionary item {i}: {type(stock)}")
                continue
                
            symbol = stock.get('symbol', 'Unknown')
            print(f"📤 Sending detailed analysis {i}/{len(stocks)}: {symbol}")
            if self._send_detailed_stock_analysis(webhook_url, stock):
                successful_stocks += 1

        # Send completion message
        self._send(webhook_url, {"content": f"✅ **Analysis Complete** - {successful_stocks}/{len(stocks)} comprehensive stock reports sent successfully!"})

        success_msg = f"✅ SUCCESS: {successful_stocks}/{len(stocks)} comprehensive stock reports sent to Discord!"
        print(success_msg)
        return success_msg

    def _send(self, webhook_url: str, payload: dict):
        try:
            response = requests.post(webhook_url, json=payload, timeout=15)
            print(f"📨 Discord Response: {response.status_code}")
            
            # 200 or 204 both mean success for Discord
            if response.status_code in (200, 204):
                return True
            else:
                print(f"❌ FAILED → Status: {response.status_code} | Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ EXCEPTION → {e}")
            return False

    def _send_comprehensive_summary(self, webhook_url: str, stocks: list):
        # Safely count actions
        counts = {
            "STRONG BUY": 0,
            "BUY": 0,
            "HOLD": 0,
            "CAUTIOUS": 0,
            "SELL": 0,
        }
        
        total_score = 0
        high_confidence_stocks = []
        
        for stock in stocks:
            if not isinstance(stock, dict):
                continue
                
            action = stock.get("action", stock.get("recommendation", ""))
            symbol = stock.get("symbol", "Unknown")
            score = stock.get("total_score", stock.get("totalInvestmentScore", 0))
            confidence = stock.get("confidence", stock.get("confidenceLevel", ""))
            
            total_score += score
            
            if "STRONG BUY" in action or "🚀" in action:
                counts["STRONG BUY"] += 1
            elif "BUY" in action or "📈" in action:
                counts["BUY"] += 1
            elif "HOLD" in action or "⚖️" in action:
                counts["HOLD"] += 1
            elif "CAUTIOUS" in action or "⚠️" in action:
                counts["CAUTIOUS"] += 1
            elif "SELL" in action or "📉" in action:
                counts["SELL"] += 1
                
            if confidence in ["HIGH", "VERY HIGH"]:
                high_confidence_stocks.append(symbol)

        avg_score = total_score / len(stocks) if stocks else 0
        
        # Create comprehensive summary embed
        embed = {
            "title": "📊 COMPREHENSIVE AI STOCK INTELLIGENCE REPORT",
            "description": f"**Detailed Analysis of {len(stocks)} Top Stocks** • {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "color": 0x0099ff,
            "fields": [
                {"name": "🚀 Strong Buy", "value": f"**{counts['STRONG BUY']}** stocks", "inline": True},
                {"name": "📈 Buy", "value": f"**{counts['BUY']}** stocks", "inline": True},
                {"name": "⚖️ Hold", "value": f"**{counts['HOLD']}** stocks", "inline": True},
                {"name": "⚠️ Cautious", "value": f"**{counts['CAUTIOUS']}** stocks", "inline": True},
                {"name": "📉 Sell", "value": f"**{counts['SELL']}** stocks", "inline": True},
                {"name": "📊 Total Analyzed", "value": f"**{len(stocks)}** stocks", "inline": True},
                {"name": "🎯 Average Score", "value": f"**{avg_score:.1f}/100**", "inline": True},
                {"name": "🛡 High Confidence", "value": f"**{len(high_confidence_stocks)}** stocks", "inline": True},
                {"name": "⭐ Top Picks", "value": ", ".join(high_confidence_stocks) if high_confidence_stocks else "None", "inline": True},
            ],
            "footer": {"text": "Detailed individual analysis follows..."}
        }
        self._send(webhook_url, {"embeds": [embed]})

    def _send_detailed_stock_analysis(self, webhook_url: str, stock: dict):
        if not isinstance(stock, dict):
            return False
            
        symbol = stock.get("symbol", "N/A")
        action = stock.get("action", stock.get("recommendation", "N/A"))
        score = stock.get("total_score", stock.get("totalInvestmentScore", 0))
        confidence = stock.get("confidence", stock.get("confidenceLevel", "N/A"))
        
        # Color mapping
        if "STRONG BUY" in action or "🚀" in action:
            color = 0x00FF00
        elif "BUY" in action or "📈" in action:
            color = 0x1aff66
        elif "HOLD" in action or "⚖️" in action:
            color = 0xcccc00
        elif "CAUTIOUS" in action or "⚠️" in action:
            color = 0xff9933
        elif "SELL" in action or "📉" in action:
            color = 0xFF0000
        else:
            color = 0x808080

        # Create multiple embeds for comprehensive data
        embeds = []
        
        # Main stock analysis embed
        main_fields = [
            {"name": "🎯 Investment Score", "value": f"**{score}/100**", "inline": True},
            {"name": "🛡 Confidence Level", "value": f"**{confidence}**", "inline": True},
            {"name": "📈 Recommendation", "value": f"**{action}**", "inline": True},
        ]
        
        # Add categories if available
        categories = []
        for key in ["valuationCategory", "growthCategory", "momentumCategory", "financialHealthCategory", "marketPositionCategory"]:
            if stock.get(key):
                categories.append(f"**{key.replace('Category', '')}**: {stock[key]}")
        
        if categories:
            main_fields.append({"name": "📊 Categories", "value": "\n".join(categories), "inline": False})
        
        main_embed = {
            "title": f"📈 {symbol} - COMPREHENSIVE ANALYSIS",
            "color": color,
            "fields": main_fields,
            "timestamp": datetime.utcnow().isoformat()
        }
        embeds.append(main_embed)
        
        # Investment Thesis Embed
        if stock.get("investmentThesis"):
            thesis_embed = {
                "title": f"💭 {symbol} - Investment Thesis",
                "color": color,
                "description": stock["investmentThesis"],
                "timestamp": datetime.utcnow().isoformat()
            }
            embeds.append(thesis_embed)
        
        # Strengths and Concerns Embed
        strengths_concerns_fields = []
        
        if stock.get("keyStrengths") and isinstance(stock["keyStrengths"], list):
            strengths = "\n".join(f"✅ {s}" for s in stock["keyStrengths"])
            strengths_concerns_fields.append({"name": "🌟 Key Strengths", "value": strengths, "inline": False})
        
        if stock.get("concerns") and isinstance(stock["concerns"], list):
            concerns = "\n".join(f"⚠️ {c}" for c in stock["concerns"])
            strengths_concerns_fields.append({"name": "🚨 Key Concerns", "value": concerns, "inline": False})
        
        if strengths_concerns_fields:
            strengths_embed = {
                "title": f"📋 {symbol} - Strengths & Concerns",
                "color": color,
                "fields": strengths_concerns_fields,
                "timestamp": datetime.utcnow().isoformat()
            }
            embeds.append(strengths_embed)
        
        # News Summary Embed
        if stock.get("summary") and stock["summary"] != "No recent news articles found.":
            # Truncate summary if too long
            summary = stock["summary"]
            if len(summary) > 2000:
                summary = summary[:2000] + "..."
            
            news_embed = {
                "title": f"📰 {symbol} - Recent News Summary",
                "color": color,
                "description": summary,
                "timestamp": datetime.utcnow().isoformat()
            }
            embeds.append(news_embed)
        
        # Additional Info Embed
        additional_fields = []
        
        if stock.get("ipoStatus"):
            additional_fields.append({"name": "🏛 IPO Status", "value": stock["ipoStatus"], "inline": True})
        
        if stock.get("analysisTimestamp"):
            additional_fields.append({"name": "🕒 Analysis Time", "value": stock["analysisTimestamp"][:10], "inline": True})
        
        if additional_fields:
            info_embed = {
                "title": f"ℹ️ {symbol} - Additional Information",
                "color": color,
                "fields": additional_fields,
                "timestamp": datetime.utcnow().isoformat()
            }
            embeds.append(info_embed)
        
        # Send all embeds for this stock
        return self._send(webhook_url, {"embeds": embeds})

    def _send_stock(self, webhook_url: str, stock: dict):
        """Legacy method - keeping for compatibility"""
        return self._send_detailed_stock_analysis(webhook_url, stock)

    def _send_summary(self, webhook_url: str, stocks: list):
        """Legacy method - keeping for compatibility"""
        self._send_comprehensive_summary(webhook_url, stocks)


# Test the tool directly
if __name__ == "__main__":
    print("🧪 TESTING COMPREHENSIVE NOTIFIER TOOL DIRECTLY")
    print("=" * 60)
    
    tool = DiscordNotifierTool()
    result = tool._run()
    print(f"🎯 TEST RESULT: {result}")