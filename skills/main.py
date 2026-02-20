#!/usr/bin/env python3
"""
Aftermath x TradingView Trading Bot
Main entry point for the trading system

Usage:
    python3 main.py --symbol BTCUSD --timeframe 5m
    
Environment variables:
    WALLET_PRIVATE_KEY: Your Sui wallet private key
    TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_CHAT_ID: For alerts
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime

# Add skills directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aftermath_bot import AftermathBot, CONFIG
from tradingview_reader import CHART_CONFIG, calculate_signal


async def parse_tradingview_browser(tab_id: str, browser) -> dict:
    """
    Parse TradingView chart from browser tab.
    Reads current price, EMA, and RSI from the visible chart.
    """
    # This would use browser automation
    # For now, return placeholder that matches Hector's current chart
    
    return {
        "symbol": "BTCUSD",
        "price": 67300.92,  # From current chart
        "ema_9": 67129.92,  # From current chart
        "rsi": 50,  # Would need to read from indicator panel
        "ohlc": {
            "open": 67079.62,
            "high": 67458.00,
            "low": 67076.30,
            "close": 67300.92
        },
        "timestamp": datetime.now().isoformat()
    }


async def main():
    parser = argparse.ArgumentParser(description="Aftermath Trading Bot")
    parser.add_argument("--symbol", default="BTCUSD", help="Trading symbol")
    parser.add_argument("--timeframe", default="5m", help="Timeframe")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║        Aftermath x TradingView Futures Trading Bot         ║
╠════════════════════════════════════════════════════════════╣
║  Symbol: {args.symbol}                                          ║
║  Timeframe: {args.timeframe}                                           ║
║  Mode: {'DRY RUN' if args.dry_run else 'LIVE TRADING'}                                      ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize bot
    bot = AftermathBot(CONFIG)
    
    if not args.dry_run and not CONFIG.get("private_key"):
        print("ERROR: No private key set. Set WALLET_PRIVATE_KEY env var or use --dry-run")
        sys.exit(1)
    
    print(f"Initialized bot with wallet: {CONFIG['wallet_address'][:10]}...")
    
    # Main trading loop
    print(f"\nStarting main loop for {args.symbol} on {args.timeframe}...")
    print("Press Ctrl+C to stop\n")
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Iteration {iteration}")
            
            # In production, this would read from browser:
            # chart_data = await parse_tradingview_browser(tab_id, browser)
            
            # For now, use placeholder (replace with actual browser read)
            chart_data = {
                "symbol": args.symbol,
                "price": 67300.92,
                "ema_9": 67129.92,
                "rsi": 50,
                "ohlc": {
                    "open": 67079.62,
                    "high": 67458.00,
                    "low": 67076.30,
                    "close": 67300.92
                }
            }
            
            # Calculate signal
            signal = calculate_signal(
                chart_data["price"],
                chart_data["ema_9"],
                chart_data["rsi"]
            )
            
            print(f"  Price: ${chart_data['price']:,.2f}")
            print(f"  EMA9:  ${chart_data['ema_9']:,.2f}")
            print(f"  RSI:   {chart_data['rsi']}")
            print(f"  Signal: {signal['direction'].upper()} (strength: {signal['strength']:.2f})")
            print(f"  Reason: {signal['reason']}")
            
            # Execute based on signal
            if not args.dry_run:
                if signal["direction"] != "neutral" and signal["strength"] > 0.7:
                    if not bot.position:
                        # Open new position
                        print(f"  → Opening {signal['direction']} position...")
                        # await bot.open_position(
                        #     signal["direction"],
                        #     100,  # size
                        #     chart_data["price"]
                        # )
                    else:
                        # Check exit conditions
                        print(f"  → Checking exit conditions...")
                        # await bot.check_stop_loss(chart_data["price"])
                        # await bot.check_take_profit(chart_data["price"])
            
            # Wait before next iteration
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        
        # Close any open positions
        if bot.position:
            print("Closing open position...")
            # await bot.close_position(current_price)


if __name__ == "__main__":
    asyncio.run(main())
