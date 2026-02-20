# TradingView Chart Reader
# Reads current chart values from TradingView browser tab
# Works with Aftermath Bot - Real-time Dynamic Updates

import json
import re
from typing import Optional, Dict

# TradingView indicator mappings
INDICATOR_NAMES = {
    "EMA": ["EMA", "Exponential Moving Average", "EMA 9"],
    "RSI": ["RSI", "Relative Strength Index"],
    "MTI": ["MTI", "Market Trend Indicator"],
    "MFI": ["MFI", "Money Flow Index"]
}


async def read_tradingview_browser(browser, tab_id: str) -> Dict:
    """
    Read live data from TradingView browser tab.
    
    This function:
    1. Takes a snapshot of the TradingView chart tab
    2. Parses current price, EMA, RSI from the DOM
    3. Returns structured data for the bot
    
    Requires: TradingView tab to be open and visible
    """
    from datetime import datetime
    
    result = {
        "symbol": "BTCUSD",
        "price": 0,
        "ohlc": {},
        "ema_9": 0,
        "rsi": 50,
        "trend": "neutral",
        "support": [],
        "resistance": [],
        "timestamp": datetime.now().isoformat(),
        "source": "browser"
    }
    
    try:
        # Get snapshot of TradingView tab
        snapshot = browser.snapshot(tab_id)
        
        # Parse price from chart - look for price display
        # TradingView typically shows price in specific elements
        price_text = find_element_text(snapshot, ["price", "last", "close"])
        if price_text:
            result["price"] = parse_price(price_text)
        
        # Parse EMA from indicators panel
        ema_text = find_element_text(snapshot, ["EMA", "ema", "exponential"])
        if ema_text:
            result["ema_9"] = parse_price(ema_text)
        
        # Parse RSI
        rsi_text = find_element_text(snapshot, ["RSI", "rsi"])
        if rsi_text:
            result["rsi"] = parse_rsi(rsi_text)
            
        # Try to find support/resistance levels (horizontal lines)
        # These are typically drawn as trendlines or price alerts
        result["support"] = find_support_levels(snapshot)
        result["resistance"] = find_resistance_levels(snapshot)
        
    except Exception as e:
        print(f"Error reading TradingView: {e}")
        
    return result


def find_element_text(snapshot: dict, keywords: list) -> Optional[str]:
    """Search snapshot for element containing keywords"""
    # Recursively search the snapshot tree
    text = snapshot.get("text", "")
    if any(kw.lower() in text.lower() for kw in keywords):
        return text
    for child in snapshot.get("children", []):
        result = find_element_text(child, keywords)
        if result:
            return result
    return None


def parse_price(text: str) -> float:
    """Extract price from text like '$67,961' or '67,961.50'"""
    # Remove $ and commas
    cleaned = text.replace("$", "").replace(",", "").strip()
    # Extract first number
    match = re.search(r'[\d.]+', cleaned)
    if match:
        try:
            return float(match.group())
        except:
            pass
    return 0


def parse_rsi(text: str) -> float:
    """Extract RSI value from text"""
    # Look for number between 0-100
    match = re.search(r'(\d+\.?\d*)\s*(?=|$)', text)
    if match:
        try:
            val = float(match.group(1))
            if 0 <= val <= 100:
                return val
        except:
            pass
    return 50


def find_support_levels(snapshot: dict) -> list:
    """Find horizontal support lines on chart"""
    # This would look for specific DOM elements
    # In practice, you'd need to parse drawn lines
    return []


def find_resistance_levels(snapshot: dict) -> list:
    """Find horizontal resistance lines on chart"""
    return []


# Fallback: Default strategy levels (from your analysis)
TRADING_LEVELS = {
    "BTCUSDT": {
        "bias_score": 0,
        "recommendation": "short",
        "long_level": 68072.6,
        "short_level": 68465,
        "tp1": 67680.2,
        "tp2": 66870,
        "risk_reward": 2.52,
        "models": {
            "arcturus": {"match": 1.0, "active": True},
            "dopamine": {"match": 0.83, "active": False},
            "volume_seer": {"match": 0.67, "active": False},
            "sniper": {"match": 0.63, "active": False}
        }
    }
}


def parse_chart_data_from_snapshot(snapshot: dict) -> Dict:
    """
    Parse chart data from TradingView snapshot.
    
    Extracts:
    - Current price (last close)
    - OHLC values
    - EMA values
    - RSI values
    - Any visible support/resistance levels
    """
    result = {
        "symbol": "BTCUSD",
        "price": 0,
        "ohlc": {},
        "ema_9": 0,
        "rsi": 50,
        "trend": "neutral",
        "support": [],
        "resistance": []
    }
    
    # Parse from snapshot text/elements
    # This is a simplified version - actual implementation
    # would parse the specific DOM elements
    
    return result


def calculate_signal(price: float, ema_9: float, rsi: float = 50, symbol: str = "BTCUSDT") -> Dict:
    """
    Calculate trading signal from indicators + strategy levels.
    
    Returns:
    - direction: "long", "short", or "neutral"
    - strength: 0.0 to 1.0
    - entry_price: suggested entry
    - stop_loss: suggested stop loss
    - take_profit: suggested take profit
    """
    signal = {
        "direction": "neutral",
        "strength": 0.0,
        "entry_price": price,
        "stop_loss": 0,
        "take_profit": 0,
        "reason": ""
    }
    
    # Get strategy levels for symbol
    levels = TRADING_LEVELS.get(symbol, {})
    
    # Use bias score from strategy (0 = bearish, 10 = bullish)
    bias_score = levels.get("bias_score", 5)
    recommendation = levels.get("recommendation", "neutral")
    
    # Calculate distance from EMA
    ema_distance = ((price - ema_9) / ema_9) * 100
    
    # Primary signal from strategy recommendation
    if recommendation == "short" and bias_score <= 3:
        # Bearish - look for short entries
        if price >= levels.get("short_level", price * 1.01):
            signal["direction"] = "short"
            signal["strength"] = min(1.0, 0.7 + (bias_score / 20))
            signal["stop_loss"] = levels.get("long_level", price * 1.01)
            signal["take_profit"] = levels.get("tp1", price * 0.98)
            signal["reason"] = f"Bearish bias ({bias_score}/10), price at resistance"
        elif price <= levels.get("long_level", price * 0.99):
            signal["direction"] = "neutral"
            signal["reason"] = "Price at support - wait for entry zone"
            
    elif recommendation == "long" and bias_score >= 7:
        # Bullish - look for long entries
        if price <= levels.get("long_level", price * 0.99):
            signal["direction"] = "long"
            signal["strength"] = min(1.0, 0.7 + (bias_score / 20))
            signal["stop_loss"] = levels.get("short_level", price * 0.99)
            signal["take_profit"] = levels.get("tp1", price * 1.02)
            signal["reason"] = f"Bullish bias ({bias_score}/10), price at support"
            
    # Fallback to EMA-based signals if no strategy
    elif levels:
        # Long signal: price above EMA + RSI in favorable zone
        if price > ema_9 and 30 < rsi < 70:
            signal["direction"] = "long"
            signal["strength"] = min(1.0, (ema_distance / 2) + 0.3)
            signal["stop_loss"] = ema_9  # Stop at EMA
            signal["take_profit"] = price * 1.05  # 5% target
            signal["reason"] = f"Price {ema_distance:.2f}% above EMA, RSI at {rsi}"
            
        # Short signal: price below EMA + RSI in favorable zone
        elif price < ema_9 and 30 < rsi < 70:
            signal["direction"] = "short"
            signal["strength"] = min(1.0, (abs(ema_distance) / 2) + 0.3)
            signal["stop_loss"] = ema_9
            signal["take_profit"] = price * 0.95
            signal["reason"] = f"Price {abs(ema_distance):.2f}% below EMA, RSI at {rsi}"
    
    # Neutral
    else:
        signal["reason"] = "No clear direction - price near EMA or RSI in overbought/oversold"
        
    return signal


# Browser integration functions
async def read_tradingview_tab(browser_tab_id: str) -> Optional[Dict]:
    """
    Read current values from TradingView tab.
    
    This function would use browser automation to:
    1. Navigate to the chart
    2. Read indicator values from the DOM
    3. Parse OHLC from the chart
    4. Return structured data
    """
    # Placeholder - actual implementation would use browser tool
    # to read specific elements from TradingView
    
    # Example of what we'd look for:
    # - Current price: found in price display
    # - EMA: found in indicator panel
    # - RSI: found in indicator panel
    
    return None


# Configuration for Hector's chart
CHART_CONFIG = {
    "symbols": ["BTCUSD", "SOLUSDT", "SUIUSD"],
    "timeframes": ["5m", "15m", "1h", "4h"],
    "default_symbol": "BTCUSD",
    "default_timeframe": "5m",
    # Hector's current indicators
    "indicators": {
        "EMA": {"length": 9},
        "RSI": {"length": 7, "low": 30, "high": 70},
        "MTI": {}  # Market Trend Indicator
    }
}
