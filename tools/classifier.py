from crewai.tools import BaseTool
import json
import numpy as np
import os
from datetime import datetime
from typing import Dict, List, Any

# Hardcoded paths for compatibility
INPUT = r"C:\Users\Admin\Desktop\crewai-1\crewai\data\stock_analysis.json"
OUTPUT = r"C:\Users\Admin\Desktop\crewai-1\crewai\data\classified_stocks.json"

class StockClassifierTool(BaseTool):
    name: str = "stock_classifier_tool"
    description: str = "Classifies stocks into BUY/SELL/HOLD recommendations using comprehensive multi-factor analysis"
    
    def _run(self, input_file: str = None, output_file: str = None) -> str:
        """Execute stock classification analysis"""
        input_path = input_file or INPUT
        output_path = output_file or OUTPUT
        
        if not os.path.exists(input_path):
            return f"❌ Input file not found: {input_path}"

        print("🔍 Loading stock data...")
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                stock_data = json.load(f)
        except Exception as e:
            return f"❌ Error loading data: {e}"

        classifier = StockClassifier()
        results = []
        
        print(f"📈 Analyzing {len(stock_data)} stocks...")
        
        for metrics in stock_data:
            result = classifier.classify(metrics)
            results.append(result)

        # Save results wrapped in classified_stocks object
        output_data = {
            "classified_stocks": results
        }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            return f"❌ Error saving results: {e}"

        return f"✅ Stock classification completed. Analyzed {len(stock_data)} stocks. Results saved to: {output_path}"


class StockClassifier:
    """PERFECTED Stock Classification System"""
    
    def __init__(self):
        self.scoring_weights = {
            'valuation': 0.30,
            'growth': 0.25,
            'momentum': 0.22,
            'financial_health': 0.18,
            'market_position': 0.05
        }
        
        self.action_thresholds = {
            'STRONG_BUY': 65,
            'BUY': 45,
            'HOLD': 25,
            'CAUTIOUS': 10,
            'SELL': -5
        }

    def safe_float(self, value):
        """Safely convert to float with NaN handling"""
        if value is None or value == "None" or value == "":
            return None
        try:
            result = float(value)
            return result if not np.isnan(result) else None
        except (TypeError, ValueError):
            return None

    def is_new_ipo(self, metrics):
        critical_metrics = ["pe", "pb", "rev_g", "pm", "roe", "debt_e", "current_ratio"]
        missing_count = sum(1 for k in critical_metrics if self.safe_float(metrics.get(k)) is None)
        return missing_count >= 4

    def calculate_confidence(self, evaluations: List[Dict], total_score: float) -> int:
        base_confidence = min(80, max(40, int(abs(total_score) * 0.9)))
        strong_categories = sum(1 for e in evaluations if e['score'] > 15)
        consistency_boost = strong_categories * 5
        data_categories = sum(1 for e in evaluations if len(e['reasons']) > 2)
        data_boost = min(20, data_categories * 4)
        confidence = base_confidence + consistency_boost + data_boost
        return min(95, max(45, confidence))

    def _generate_investment_thesis(self, action: str, strengths: List[str], 
                                  concerns: List[str], total_score: float) -> str:
        if action in ["STRONG BUY 🚀", "BUY 📈"]:
            if total_score > 55:
                thesis = "High-conviction opportunity with "
            else:
                thesis = "Compelling investment case with "
            
            if strengths:
                key_points = [s.split(" - ")[0] if " - " in s else s for s in strengths[:2]]
                thesis += " and ".join(key_points)
                thesis += ". This combination creates a favorable risk-reward setup."
            else:
                thesis = "Positive fundamentals outweigh current concerns for potential appreciation."
        
        elif action == "HOLD ⚖️":
            thesis = "Balanced profile suggests maintaining current position while monitoring for "
            thesis += "improved fundamentals or technical confirmation before adding exposure."
        
        else:
            thesis = "Current risk factors suggest caution. Consider waiting for "
            thesis += "improved conditions or clearer positive catalysts before investment."
        
        return thesis

    def _get_category_label(self, score: float) -> str:
        """Convert numerical score to category label"""
        if score >= 50:
            return "EXCELLENT"
        elif score >= 40:
            return "STRONG" 
        elif score >= 30:
            return "FAVORABLE"
        elif score >= 20:
            return "MODERATE"
        elif score >= 10:
            return "WEAK"
        else:
            return "POOR"

    def _get_confidence_level(self, confidence_score: int) -> str:
        """Convert confidence score to level"""
        if confidence_score >= 80:
            return "HIGH"
        elif confidence_score >= 60:
            return "MODERATE"
        else:
            return "LOW"

    def _handle_ipo_case(self, metrics) -> Dict[str, Any]:
        symbol = metrics.get("symbol", "UNKNOWN")
        reasons = ["📋 Limited fundamental history - recent IPO"]
        strengths = []
        
        target_upside = self.safe_float(metrics.get("target_upside"))
        price_change = self.safe_float(metrics.get("price_change"))
        rev_g = self.safe_float(metrics.get("rev_g"))
        
        if target_upside and target_upside > 30:
            strength = f"Strong analyst support: {target_upside:.1f}% upside potential"
            reasons.append(f"🎯 Analyst optimism: {target_upside:.1f}% upside")
            strengths.append(strength)
        
        if price_change and price_change > 15:
            strength = f"Strong early momentum: +{price_change:.1f}% post-IPO performance"
            reasons.append(f"📈 Positive early trading: +{price_change:.1f}%")
            strengths.append(strength)

        if rev_g and rev_g > 25:
            strength = f"Impressive growth trajectory: +{rev_g:.1f}% revenue growth"
            reasons.append(f"🚀 Strong growth: +{rev_g:.1f}% revenue")
            strengths.append(strength)

        return {
            "stock_symbol": symbol,
            "action_recommendation": "MONITOR 👀",
            "action_explanation": "Early-stage company - requires more operational history",
            "investment_thesis": "Promising early indicators but limited track record warrants careful observation before investment.",
            "total_investment_score": 20,
            "confidence_level": "LOW",
            "valuation_category": "INSUFFICIENT_DATA",
            "growth_category": "INSUFFICIENT_DATA",
            "momentum_category": "INSUFFICIENT_DATA",
            "financial_health_category": "INSUFFICIENT_DATA",
            "market_position_category": "INSUFFICIENT_DATA",
            "key_strengths": strengths,
            "concerns": ["Limited financial history", "IPO volatility typical", "Early-stage execution risk"],
            "analysis_timestamp": datetime.now().isoformat(),
            "ipo_status": "Recent IPO"
        }

    def evaluate_valuation(self, metrics) -> Dict[str, Any]:
        """PERFECTED valuation analysis with sector awareness"""
        score = 0
        reasons = []
        strengths = []
        details = {}

        pe = self.safe_float(metrics.get("pe"))
        pb = self.safe_float(metrics.get("pb"))
        target_upside = self.safe_float(metrics.get("target_upside"))
        ps = self.safe_float(metrics.get("ps"))
        ev_ebitda = self.safe_float(metrics.get("ev_ebitda"))

        # PERFECTED P/E Analysis with sector context
        if pe and pe > 0:
            if pe < 10:
                score += 28
                strength = f"Deep value P/E of {pe:.1f} - significantly undervalued relative to market"
                reasons.append("💰 Exceptional P/E value - deep undervaluation")
                strengths.append(strength)
                details['pe_rating'] = 'Exceptional Value'
            elif pe < 15:
                score += 20
                strength = f"Attractive P/E of {pe:.1f} - trading below fair value"
                reasons.append("💰 Attractive P/E - good value opportunity")
                strengths.append(strength)
                details['pe_rating'] = 'Attractive'
            elif pe < 22:
                score += 12
                reasons.append("📊 Reasonable P/E - fair valuation")
                details['pe_rating'] = 'Fair'
            elif pe < 35:
                score += 3
                reasons.append("⚖️ Elevated P/E - growth premium")
                details['pe_rating'] = 'Growth Premium'
            else:
                score -= 10
                reasons.append("⚠️ Excessive P/E - high risk of overvaluation")
                details['pe_rating'] = 'Overvalued'
            details['pe'] = pe

        # PERFECTED Price-to-Book with value zone detection
        if pb:
            if pb < 0.8:
                score += 22
                strength = f"Trading at {pb:.1f}P/B - significant discount to book value"
                reasons.append("🎯 Deep value P/B - strong margin of safety")
                strengths.append(strength)
                details['pb_rating'] = 'Deep Value'
            elif pb < 1.5:
                score += 16
                strength = f"Reasonable {pb:.1f}P/B - good fundamental value"
                reasons.append("📊 Solid P/B value")
                strengths.append(strength)
                details['pb_rating'] = 'Good Value'
            elif pb < 3.0:
                score += 8
                reasons.append("📊 Moderate P/B - growth expectations")
                details['pb_rating'] = 'Growth Priced'
            elif pb > 6.0:
                score -= 8
                reasons.append("⚠️ High P/B - speculative valuation")
                details['pb_rating'] = 'Speculative'
            details['pb'] = pb

        # PERFECTED Price-to-Sales analysis
        if ps and ps > 0:
            if ps < 1.5:
                score += 12
                strength = f"Efficient {ps:.1f}P/S - strong revenue valuation"
                reasons.append("📊 Excellent price-to-sales efficiency")
                strengths.append(strength)
            elif ps < 3.0:
                score += 6
                reasons.append("📊 Reasonable price-to-sales")
            elif ps > 8.0:
                score -= 6
                reasons.append("⚠️ High price-to-sales ratio")
            details['ps'] = ps

        # PERFECTED EV/EBITDA analysis
        if ev_ebitda and ev_ebitda > 0:
            if ev_ebitda < 8:
                score += 14
                strength = f"Strong {ev_ebitda:.1f} EV/EBITDA - operational efficiency"
                reasons.append("📊 Excellent enterprise value efficiency")
                strengths.append(strength)
            elif ev_ebitda < 12:
                score += 8
                reasons.append("📊 Good EV/EBITDA multiple")
            details['ev_ebitda'] = ev_ebitda

        # PERFECTED Analyst target analysis
        if target_upside:
            if target_upside > 40:
                score += 25
                strength = f"Strong analyst conviction: {target_upside:.1f}% upside potential"
                reasons.append(f"🚀 Exceptional analyst upside: {target_upside:.1f}%")
                strengths.append(strength)
                details['analyst_sentiment'] = 'Very Bullish'
            elif target_upside > 25:
                score += 18
                strength = f"Positive analyst outlook: {target_upside:.1f}% expected return"
                reasons.append(f"📈 Strong analyst confidence: {target_upside:.1f}%")
                strengths.append(strength)
                details['analyst_sentiment'] = 'Bullish'
            elif target_upside > 10:
                score += 10
                reasons.append(f"📊 Moderate upside: {target_upside:.1f}%")
                details['analyst_sentiment'] = 'Positive'
            elif target_upside < -20:
                score -= 15
                reasons.append(f"🔻 Significant downside risk: {abs(target_upside):.1f}%")
                details['analyst_sentiment'] = 'Bearish'
            details['target_upside'] = target_upside

        return {
            "score": min(70, score),
            "reasons": reasons,
            "strengths": strengths,
            "details": details,
            "category": "Valuation"
        }

    def evaluate_growth(self, metrics) -> Dict[str, Any]:
        """PERFECTED growth analysis with quality focus"""
        score = 0
        reasons = []
        strengths = []
        details = {}

        rev_g = self.safe_float(metrics.get("rev_g"))
        pm = self.safe_float(metrics.get("pm"))
        roe = self.safe_float(metrics.get("roe"))
        eps_g = self.safe_float(metrics.get("eps_g"))
        opm = self.safe_float(metrics.get("opm"))

        # PERFECTED Revenue growth with quality assessment
        if rev_g is not None:
            if rev_g > 30:
                score += 25
                strength = f"Hyper-growth revenue: +{rev_g:.1f}% YoY - exceptional expansion"
                reasons.append(f"🚀 Exceptional revenue growth: +{rev_g:.1f}%")
                strengths.append(strength)
                details['revenue_growth'] = 'Hyper-Growth'
            elif rev_g > 20:
                score += 20
                strength = f"Rapid revenue growth: +{rev_g:.1f}% YoY - strong momentum"
                reasons.append(f"📈 Strong revenue growth: +{rev_g:.1f}%")
                strengths.append(strength)
                details['revenue_growth'] = 'Rapid Growth'
            elif rev_g > 12:
                score += 14
                strength = f"Solid growth: +{rev_g:.1f}% YoY - sustainable expansion"
                reasons.append(f"📊 Solid revenue growth: +{rev_g:.1f}%")
                strengths.append(strength)
                details['revenue_growth'] = 'Solid Growth'
            elif rev_g > 5:
                score += 8
                reasons.append(f"📊 Moderate growth: +{rev_g:.1f}%")
                details['revenue_growth'] = 'Moderate'
            elif rev_g < -15:
                score -= 20
                reasons.append(f"🔻 Severe revenue decline: {rev_g:.1f}%")
                details['revenue_growth'] = 'Severe Decline'
            elif rev_g < 0:
                score -= 12
                reasons.append(f"⚠️ Revenue contraction: {rev_g:.1f}%")
                details['revenue_growth'] = 'Declining'
            details['revenue_growth_pct'] = rev_g

        # PERFECTED EPS growth analysis
        if eps_g is not None:
            if eps_g > 25:
                score += 18
                strength = f"Explosive EPS growth: +{eps_g:.1f}% - accelerating profitability"
                reasons.append(f"📈 Exceptional EPS growth: +{eps_g:.1f}%")
                strengths.append(strength)
            elif eps_g > 15:
                score += 12
                strength = f"Strong EPS growth: +{eps_g:.1f}% - improving earnings"
                reasons.append(f"📈 Strong EPS growth: +{eps_g:.1f}%")
                strengths.append(strength)
            elif eps_g > 8:
                score += 8
                reasons.append(f"📊 Positive EPS growth: +{eps_g:.1f}%")
            elif eps_g < -20:
                score -= 15
                reasons.append(f"🔻 Severe EPS decline: {eps_g:.1f}%")
            details['eps_growth'] = eps_g

        # PERFECTED Profit margin analysis
        if pm is not None:
            if pm > 25:
                score += 20
                strength = f"Elite {pm:.1f}% net margins - superior profitability"
                reasons.append(f"💰 Exceptional profit margins: {pm:.1f}%")
                strengths.append(strength)
                details['profitability'] = 'Elite'
            elif pm > 18:
                score += 16
                strength = f"Strong {pm:.1f}% net margins - high quality business"
                reasons.append(f"💰 Strong profitability: {pm:.1f}%")
                strengths.append(strength)
                details['profitability'] = 'Strong'
            elif pm > 12:
                score += 12
                strength = f"Good {pm:.1f}% net margins - healthy operations"
                reasons.append(f"📊 Good profit margins: {pm:.1f}%")
                strengths.append(strength)
                details['profitability'] = 'Good'
            elif pm > 5:
                score += 6
                reasons.append(f"📊 Reasonable margins: {pm:.1f}%")
                details['profitability'] = 'Reasonable'
            elif pm < 0:
                score -= 15
                reasons.append(f"🔻 Negative margins: {pm:.1f}% - unprofitable")
                details['profitability'] = 'Unprofitable'
            details['profit_margin_pct'] = pm

        # PERFECTED Operating margin analysis
        if opm and opm > 20:
            score += 10
            strength = f"Strong {opm:.1f}% operating margins - core business efficiency"
            reasons.append("📊 Excellent operating margins")
            strengths.append(strength)

        # PERFECTED ROE analysis with quality focus
        if roe is not None:
            if roe > 25:
                score += 16
                strength = f"Outstanding {roe:.1f}% ROE - exceptional capital allocation"
                reasons.append(f"🎯 Outstanding ROE: {roe:.1f}%")
                strengths.append(strength)
                details['roe_quality'] = 'Outstanding'
            elif roe > 18:
                score += 12
                strength = f"Strong {roe:.1f}% ROE - efficient capital use"
                reasons.append(f"🎯 Strong ROE: {roe:.1f}%")
                strengths.append(strength)
                details['roe_quality'] = 'Strong'
            elif roe > 12:
                score += 8
                reasons.append(f"📊 Good ROE: {roe:.1f}%")
                details['roe_quality'] = 'Good'
            elif roe < 0:
                score -= 10
                reasons.append(f"🔻 Negative ROE: {roe:.1f}% - poor capital efficiency")
                details['roe_quality'] = 'Poor'
            details['roe_pct'] = roe

        return {
            "score": min(60, score),
            "reasons": reasons,
            "strengths": strengths,
            "details": details,
            "category": "Growth"
        }

    def evaluate_momentum(self, metrics) -> Dict[str, Any]:
        """PERFECTED momentum analysis with trend confirmation"""
        score = 0
        reasons = []
        strengths = []
        details = {}

        rsi = self.safe_float(metrics.get("rsi"))
        macd = self.safe_float(metrics.get("macd"))
        signal = self.safe_float(metrics.get("signal"))
        golden_cross = metrics.get("golden_cross", 0)
        price_change = self.safe_float(metrics.get("price_change"))
        volume_spike = self.safe_float(metrics.get("volume_spike"))
        ma_50 = self.safe_float(metrics.get("ma_50"))
        ma_200 = self.safe_float(metrics.get("ma_200"))

        # PERFECTED RSI analysis with trend context
        if rsi:
            if rsi < 30:
                score += 18
                strength = f"Oversold RSI {rsi:.1f} - strong contrarian opportunity"
                reasons.append("📈 Deeply oversold - excellent entry point")
                strengths.append(strength)
                details['rsi_signal'] = 'Oversold Opportunity'
            elif rsi < 45:
                score += 14
                strength = f"Bullish RSI {rsi:.1f} - healthy uptrend momentum"
                reasons.append("📈 Bullish momentum - strong trend")
                strengths.append(strength)
                details['rsi_signal'] = 'Bullish'
            elif rsi < 55:
                score += 6
                reasons.append("📊 Neutral momentum")
                details['rsi_signal'] = 'Neutral'
            elif rsi > 70:
                score -= 10
                reasons.append("⚠️ Overbought - near-term risk")
                details['rsi_signal'] = 'Overbought'
            details['rsi'] = rsi

        # PERFECTED MACD analysis
        if macd is not None and signal is not None:
            if macd > signal:
                score += 16
                strength = "Bullish MACD crossover - confirmed upward momentum"
                reasons.append("📊 Strong MACD bullish signal")
                strengths.append(strength)
                details['macd_signal'] = 'Bullish'
            else:
                score -= 4
                reasons.append("📊 MACD momentum weakening")
                details['macd_signal'] = 'Weak'

        # PERFECTED Golden Cross significance
        if golden_cross == 1:
            score += 20
            strength = "Golden Cross confirmed - major bullish trend established"
            reasons.append("🌟 Golden Cross - strong bullish trend")
            strengths.append(strength)
            details['trend'] = 'Major Bullish'

        # PERFECTED Moving average analysis
        if ma_50 and ma_200:
            if ma_50 > ma_200:
                score += 12
                strength = f"Trading above key MAs (${ma_50:.2f} > ${ma_200:.2f}) - uptrend confirmed"
                reasons.append("📈 Above key moving averages")
                strengths.append(strength)

        # PERFECTED Price action analysis
        if price_change:
            if price_change > 15:
                score += 14
                strength = f"Powerful momentum: +{price_change:.1f}% recent gains"
                reasons.append(f"🚀 Strong price breakout: +{price_change:.1f}%")
                strengths.append(strength)
                details['price_action'] = 'Very Strong'
            elif price_change > 8:
                score += 10
                strength = f"Positive momentum: +{price_change:.1f}% upward movement"
                reasons.append(f"📈 Positive price action: +{price_change:.1f}%")
                strengths.append(strength)
                details['price_action'] = 'Positive'
            elif price_change < -10:
                score -= 8
                reasons.append(f"🔻 Price weakness: {price_change:.1f}%")
                details['price_action'] = 'Weak'

        # PERFECTED Volume analysis
        if volume_spike and volume_spike > 60:
            score += 12
            strength = f"High volume surge ({volume_spike:.1f}%) - strong institutional interest"
            reasons.append("🔊 High volume confirmation")
            strengths.append(strength)
            details['volume'] = 'Very High'

        return {
            "score": min(55, score),
            "reasons": reasons,
            "strengths": strengths,
            "details": details,
            "category": "Momentum"
        }

    def evaluate_financial_health(self, metrics) -> Dict[str, Any]:
        """PERFECTED financial health with risk assessment"""
        score = 0
        reasons = []
        strengths = []
        details = {}

        cash_to_debt = self.safe_float(metrics.get("cash_to_debt"))
        current_ratio = self.safe_float(metrics.get("current_ratio"))
        debt_e = self.safe_float(metrics.get("debt_e"))
        annual_vol = self.safe_float(metrics.get("annual_vol"))
        quick_ratio = self.safe_float(metrics.get("quick_ratio"))

        # PERFECTED Cash position analysis
        if cash_to_debt is not None:
            if cash_to_debt > 2.0:
                score += 18
                strength = f"Fortress balance sheet: {cash_to_debt:.1f}x cash-to-debt"
                reasons.append("🛡️ Exceptional cash position")
                strengths.append(strength)
                details['cash_health'] = 'Fortress'
            elif cash_to_debt > 1.2:
                score += 14
                strength = f"Strong financial position: {cash_to_debt:.1f}x cash coverage"
                reasons.append("🛡️ Strong cash coverage")
                strengths.append(strength)
                details['cash_health'] = 'Strong'
            elif cash_to_debt > 0.6:
                score += 8
                reasons.append("📊 Adequate cash position")
                details['cash_health'] = 'Adequate'
            elif cash_to_debt < 0.2:
                score -= 15
                reasons.append("🔻 Critical cash shortage")
                details['cash_health'] = 'Critical'
            details['cash_to_debt'] = cash_to_debt

        # PERFECTED Liquidity analysis
        if current_ratio is not None:
            if current_ratio > 2.5:
                score += 12
                strength = f"Excellent liquidity: {current_ratio:.1f} current ratio"
                reasons.append("💧 Exceptional liquidity")
                strengths.append(strength)
                details['liquidity'] = 'Excellent'
            elif current_ratio > 1.8:
                score += 10
                strength = f"Strong liquidity: {current_ratio:.1f} current ratio"
                reasons.append("💧 Strong liquidity")
                strengths.append(strength)
                details['liquidity'] = 'Strong'
            elif current_ratio > 1.2:
                score += 6
                reasons.append("📊 Adequate liquidity")
                details['liquidity'] = 'Adequate'
            elif current_ratio < 0.8:
                score -= 12
                reasons.append("🔻 Liquidity concerns")
                details['liquidity'] = 'Concerning'
            details['current_ratio'] = current_ratio

        # PERFECTED Quick ratio analysis
        if quick_ratio and quick_ratio > 1.5:
            score += 8
            strength = f"Strong quick ratio {quick_ratio:.1f} - immediate liquidity"
            reasons.append("💧 Strong quick ratio")
            strengths.append(strength)

        # PERFECTED Debt analysis
        if debt_e is not None:
            if debt_e < 30:
                score += 14
                strength = f"Conservative {debt_e:.1f}% debt/equity - low financial risk"
                reasons.append("⚖️ Conservative debt levels")
                strengths.append(strength)
                details['debt_management'] = 'Conservative'
            elif debt_e < 80:
                score += 8
                reasons.append("📊 Reasonable debt load")
                details['debt_management'] = 'Reasonable'
            elif debt_e > 150:
                score -= 12
                reasons.append("🔻 High debt load - elevated risk")
                details['debt_management'] = 'High Risk'
            details['debt_to_equity'] = debt_e

        # PERFECTED Volatility assessment
        if annual_vol is not None:
            if annual_vol < 20:
                score += 8
                strength = f"Low {annual_vol:.1f}% volatility - stable characteristics"
                reasons.append("📊 Low volatility - stable")
                strengths.append(strength)
                details['volatility'] = 'Low'
            elif annual_vol > 50:
                score -= 8
                reasons.append("🌊 High volatility - speculative")
                details['volatility'] = 'High'

        return {
            "score": min(40, score),
            "reasons": reasons,
            "strengths": strengths,
            "details": details,
            "category": "Financial Health"
        }

    def evaluate_market_position(self, metrics) -> Dict[str, Any]:
        """PERFECTED market positioning analysis"""
        score = 0
        reasons = []
        strengths = []
        details = {}

        d_low = self.safe_float(metrics.get("d_low"))
        one_year_return = self.safe_float(metrics.get("one_year_return"))

        # PERFECTED 52-week position analysis
        if d_low is not None:
            if d_low < 10:
                score += 10
                strength = f"Near 52W low ({d_low:.1f}% above) - significant value opportunity"
                reasons.append("🎯 Deep value zone - near 52W low")
                strengths.append(strength)
                details['position'] = 'Deep Value'
            elif d_low < 25:
                score += 6
                reasons.append("📊 Reasonable valuation zone")
                details['position'] = 'Reasonable'
            elif d_low > 85:
                score -= 6
                reasons.append("⚠️ Extended valuation - near highs")
                details['position'] = 'Extended'
            details['percent_above_low'] = d_low

        # PERFECTED Long-term performance
        if one_year_return is not None:
            if one_year_return > 40:
                score += 8
                strength = f"Strong +{one_year_return:.1f}% 1Y performance - proven track record"
                reasons.append(f"📈 Excellent 1-year performance: +{one_year_return:.1f}%")
                strengths.append(strength)
                details['long_term_trend'] = 'Excellent'
            elif one_year_return < -25:
                score -= 6
                reasons.append(f"🔻 Weak 1-year performance: {one_year_return:.1f}%")
                details['long_term_trend'] = 'Weak'

        return {
            "score": min(15, score),
            "reasons": reasons,
            "strengths": strengths,
            "details": details,
            "category": "Market Position"
        }

    def classify(self, metrics) -> Dict[str, Any]:
        """PERFECTED classification engine with optimal decision making"""
        symbol = metrics.get("symbol", "UNKNOWN")

        if self.is_new_ipo(metrics):
            return self._handle_ipo_case(metrics)

        evaluations = [
            self.evaluate_valuation(metrics),
            self.evaluate_growth(metrics),
            self.evaluate_momentum(metrics),
            self.evaluate_financial_health(metrics),
            self.evaluate_market_position(metrics)
        ]

        total_score = 0
        category_scores = {}
        all_reasons = []
        all_strengths = []

        for i, evaluation in enumerate(evaluations):
            weight = list(self.scoring_weights.values())[i]
            weighted_score = evaluation['score'] * weight
            total_score += weighted_score
            category_scores[evaluation['category']] = {
                'score': evaluation['score'],
                'weighted_score': round(weighted_score, 2),
                'details': evaluation['details']
            }
            all_reasons.extend(evaluation['reasons'])
            all_strengths.extend(evaluation.get('strengths', []))

        # Action determination
        if total_score >= self.action_thresholds['STRONG_BUY']:
            action = "STRONG BUY 🚀"
            explanation = "Exceptional investment opportunity with strong fundamentals and momentum"
        elif total_score >= self.action_thresholds['BUY']:
            action = "BUY 📈"
            explanation = "Attractive risk-reward profile with multiple positive catalysts"
        elif total_score >= self.action_thresholds['HOLD']:
            action = "HOLD ⚖️"
            explanation = "Balanced profile - maintain position while monitoring developments"
        elif total_score >= self.action_thresholds['CAUTIOUS']:
            action = "CAUTIOUS ⚠️"
            explanation = "Some concerns present - consider waiting for improved conditions"
        else:
            action = "SELL 📉"
            explanation = "Multiple risk factors suggest reducing exposure"

        confidence = self.calculate_confidence(evaluations, total_score)
        strengths = all_strengths[:5]
        concerns = [r for r in all_reasons if any(icon in r for icon in ['⚠️', '🔻', '🌊'])]
        investment_thesis = self._generate_investment_thesis(action, strengths, concerns, total_score)

        # Convert to standardized field names for the desired output format
        return {
            "stock_symbol": symbol,
            "action_recommendation": action,
            "action_explanation": explanation,
            "total_investment_score": round(total_score, 2),
            "confidence_level": self._get_confidence_level(confidence),
            "valuation_category": self._get_category_label(category_scores['Valuation']['score']),
            "growth_category": self._get_category_label(category_scores['Growth']['score']),
            "momentum_category": self._get_category_label(category_scores['Momentum']['score']),
            "financial_health_category": self._get_category_label(category_scores['Financial Health']['score']),
            "market_position_category": self._get_category_label(category_scores['Market Position']['score']),
            "key_strengths": strengths,
            "concerns": concerns[:3],
            "investment_thesis": investment_thesis,
            "analysis_timestamp": datetime.now().isoformat(),
            "ipo_status": "Publicly Traded"
        }


# Standalone execution
if __name__ == "__main__":
    tool = StockClassifierTool()
    result = tool._run()
    print(f"\n🎯 Result: {result}")