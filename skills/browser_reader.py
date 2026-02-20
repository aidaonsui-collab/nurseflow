"""
Browser-based TradingView Reader
Reads live data from your TradingView tab
"""

from typing import Dict, Optional


async def read_tradingview_tab(browser, tab_id: str) -> Dict:
    """
    Read live trading data from TradingView browser tab.
    
    This function uses OpenClaw's browser tool to:
    1. Take a snapshot of the TradingView page
    2. Extract current price from chart
    3. Read EMA/RSI from indicator panel
    4. Find support/resistance levels
    
    Args:
        browser: OpenClaw browser instance
        tab_id: ID of the TradingView tab
        
    Returns:
        dict with price, ema_9, rsi, ohlc, support, resistance
    """
    result = {
        "price": 0,
        "ema_9": 0,
        "rsi": 50,
        "ohlc": {},
        "support": [],
        "resistance": [],
        "trend": "neutral"
    }
    
    try:
        # Get snapshot of the page
        snapshot = browser.snapshot(tab_id)
        
        # Parse price - TradingView shows price in multiple places
        # Look for the main price display
        result["price"] = parse_price_from_snapshot(snapshot)
        
        # Parse EMA from indicators
        result["ema_9"] = parse_ema_from_snapshot(snapshot)
        
        # Parse RSI
        result["rsi"] = parse_rsi_from_snapshot(snapshot)
        
        # Try to find support/resistance from drawings
        result["support"], result["resistance"] = parse_sr_levels(snapshot)
        
    except Exception as e:
        print(f"Error reading TradingView: {e}")
        
    return result


def parse_price_from_snapshot(snapshot: dict) -> float:
    """
    Find and extract current price from TradingView snapshot.
    TradingView shows price in the chart header and in OHLC values.
    """
    import re
    
    # Search for price patterns in the snapshot
    # Typical: "$67,300.92" or "67,300" or "67.3K"
    
    def search_tree(node, depth=0):
        if depth > 10:  # Limit recursion
            return None
            
        text = node.get("text", "")
        
        # Look for price-like numbers near "C" (close) or "$"
        if "C" in text or "$" in text:
            # Extract numbers
            matches = re.findall(r'[\d,]+\.?\d*', text)
            for match in matches:
                num = float(match.replace(",", ""))
                if 1000 < num < 1000000:  # Reasonable BTC price range
                    return num
                    
        # Check children
        for child in node.get("children", []):
            result = search_tree(child, depth + 1)
            if result:
                return result
                
        return None
    
    return search_tree(snapshot) or 0


def parse_ema_from_snapshot(snapshot: dict) -> float:
    """Extract EMA value from indicators panel"""
    # Similar to price parsing, look for EMA-labeled elements
    import re
    
    def search_tree(node, depth=0):
        if depth > 10:
            return None
            
        text = node.get("text", "").lower()
        
        if "ema" in text or "exponential moving average" in text:
            # Extract the number after EMA label
            # Pattern: "EMA 67,129.92" or similar
            import re
            match = re.search(r'([\d,]+\.?\d*)', text)
            if match:
                return float(match.group(1).replace(",", ""))
                
        for child in node.get("children", []):
            result = search_tree(child, depth + 1)
            if result:
                return result
                
        return None
    
    return search_tree(snapshot) or 0


def parse_rsi_from_snapshot(snapshot: dict) -> float:
    """Extract RSI value from indicators panel"""
    import re
    
    def search_tree(node, depth=0):
        if depth > 10:
            return None
            
        text = node.get("text", "").lower()
        
        if "rsi" in text:
            match = re.search(r'(\d+\.?\d*)', text)
            if match:
                val = float(match.group(1))
                if 0 <= val <= 100:
                    return val
                    
        for child in node.get("children", []):
            result = search_tree(child, depth + 1)
            if result:
                return result
                
        return 50  # Default


def parse_sr_levels(snapshot: dict) -> tuple:
    """
    Find support and resistance levels from horizontal lines.
    This is complex - TradingView stores drawings in specific elements.
    """
    # For now, return empty - would need more complex parsing
    return [], []


# Demo function - simulates reading from browser
async def demo_read():
    """Demo with sample data from current chart"""
    return {
        "price": 67300.92,
        "ema_9": 67129.92,
        "rsi": 50,
        "ohlc": {
            "open": 67079.62,
            "high": 67458.00,
            "low": 67076.30,
            "close": 67300.92
        },
        "support": [66800, 66500],
        "resistance": [68000, 68500],
        "trend": "neutral"
    }
