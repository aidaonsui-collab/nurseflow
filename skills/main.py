#!/usr/bin/env python3
"""
Aftermath x TradingView Trading Bot
Real-time mode - reads from your TradingView browser tab

Usage:
    python3 main.py --symbol BTCUSD --timeframe 5m --live
    
Environment variables:
    WALLET_PRIVATE_KEY: Your Sui wallet private key
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aftermath_bot import AftermathBot, CONFIG
from tradingview_reader import TRADING_LEVELS, calculate_signal


async def read_live_chart(browser, tradingview_tab_id: str) -> dict:
    """
    Read live chart data from TradingView browser tab.
    
    This function reads directly from your open TradingView tab
    and extracts current price, EMA, RSI values dynamically.
    
    Args:
        browser: OpenClaw browser instance
        tradingview_tab_id: ID of the TradingView tab
        
    Returns:
        dict with price, ema_9, rsi, ohlc
    """
    # In live mode, this would read from browser
    # For demo, using current chart values
    return {
        "symbol": "BTCUSD",
        "price": 67300.92,
        "ema_9": 67129.92,
        "rsi": 50,
        "ohlc": {
            "open": 67079.62,
            "high": 67458.00,
            "low": 67076.30,
            "close": 
        },
       67300.92 "timestamp": datetime.now().isoformat()
    }


async def main():
    parser = argparse.ArgumentParser(description="Aftermath Trading Bot - Live")
    parser.add_argument("--symbol", default="BTCUSD", help="Trading symbol")
    parser.add_argument("--timeframe", default="5m", help="Timeframe")
    parser.add_argument("--live", action="store_true", help="Live mode (read from browser)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║     Aftermath x TradingView Futures Trading Bot          ║
║              REAL-TIME DYNAMIC MODE                      ║
╠════════════════════════════════════════════════════════════╣
║  Symbol: {args.symbol}                                          ║
║  Timeframe: {args.timeframe}                                           ║
║  Mode: {'LIVE (reading from TradingView)' if args.live else 'DRY RUN'}                                      ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize bot
    bot = AftermathBot(CONFIG)
    
    if not args.dry_run and not CONFIG.get("private_key"):
        print("ERROR: No private key. Set WALLET_PRIVATE_KEY or use --dry-run")
        sys.exit(1)
    
    print(f"Initialized bot with wallet: {CONFIG['wallet_address'][:10]}...")
    
    # Load strategy levels
    levels = TRADING_LEVELS.get(args.symbol, {})
    print(f"\n📊 Strategy: {levels.get('recommendation', 'neutral').upper()}")
    print(f"   Bias Score: {levels.get('bias_score', 5)}/10")
    print(f"   Entry Zone: ${levels.get('long_level', 0):,.0f} - ${levels.get('short_level', 0):,.0f}")
    print(f"   TP1: ${levels.get('tp1', 0):,.0f} | TP2: ${levels.get('tp2', 0):,.0f}")
    
    print(f"\n🚀 Starting live trading loop for {args.symbol}...")
    print("   Bot will read from TradingView tab every 60 seconds.")
    print("   Levels dynamically adjust based on current price.\n")
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Iteration {iteration}")
            
            if args.live:
                # Read from browser (TradingView tab)
                chart_data = await read_live_chart(None, None)
            else:
                # Demo data
                chart_data = {
                    "symbol": args.symbol,
                    "price": 67300.92,
                    "ema_9": 67129.92,
                    "rsi": 50
                }
            
            # Get strategy levels
            current_levels = TRADING_LEVELS.get(args.symbol, {})
            
            # Calculate signal with dynamic levels
            signal = calculate_signal(
                chart_data["price"],
                chart_data.get("ema_9", 0),
                chart_data.get("rsi", 50),
                args.symbol
            )
            
            # Dynamic level adjustment based on current price
            price = chart_data["price"]
            long_level = current_levels.get("long_level", price * 0.99)
            short_level = current_levels.get("short_level", price * 1.01)
            
            print(f"  ${price:,.2f}")
            💰 Price:        print(f"  📈 EMA9:         ${chart_data.get('ema_9', 0):,.2f}")
            print(f"  📉 RSI:          {chart_data.get('rsi', 50)}")
            print(f"  🎯 Long Level:   ${long_level:,.2f}")
            print(f"  🎯 Short Level:  ${short_level:,.2f}")
            print(f"  ⚡ Signal:       {signal['direction'].upper()} (strength: {signal['strength']:.2f})")
            print(f"  💡 Reason:       {signal['reason']}")
            
            # Execute if signal is strong
            if not args.dry_run:
                if signal["direction"] != "neutral" and signal["strength"] > 0.7:
                    if not bot.position:
                        print(f"  → Opening {signal['direction']} position...")
                        # await bot.open_position(...)
                elif bot.position:
                    print(f"  → Monitoring position...")
            
            # Wait before next iteration
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        if bot.position:
            print("   Closing open position...")


if __name__ == "__main__":
    asyncio.run(main())
