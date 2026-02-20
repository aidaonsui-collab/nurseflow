#!/usr/bin/env python3
"""
Bankr Trading Integration
Executes trades via Bankr AI agent based on TradingView signals

Usage:
    python3 bankr_trader.py --action buy --token ETH --amount 0.01
    python3 bankr_trader.py --action sell --token BTC --amount 0.001
    python3 bankr_trader.py --signal long --price 67000 --target 68000
"""

import os
import requests
import json
import time
import argparse
from datetime import datetime

# Bankr API configuration
BANKR_API_KEY = os.environ.get("BANKR_API_KEY", "bk_3GKNL8C5S6Z9WQEXVU6E43S92626PNZW")
BANKR_API_URL = "https://api.bankr.bot"

# TradingView signals we're tracking
TRADING_SIGNALS = {
    "BTC": {"current_price": 67000, "bias": "bearish", "strategy": "arcturus"},
    "ETH": {"current_price": 3450, "bias": "bullish", "strategy": "arcturus"},
    "SOL": {"current_price": 84, "bias": "bullish", "strategy": "arcturus"},
    "SUI": {"current_price": 0.96, "bias": "bullish", "strategy": "arcturus"},
}


def submit_prompt(prompt: str, thread_id: str = None) -> dict:
    """Submit a prompt to Bankr AI agent"""
    url = f"{BANKR_API_URL}/agent/prompt"
    headers = {
        "X-API-Key": BANKR_API_KEY,
        "Content-Type": "application/json"
    }
    data = {"prompt": prompt}
    if thread_id:
        data["threadId"] = thread_id
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def check_job(job_id: str) -> dict:
    """Check job status"""
    url = f"{BANKR_API_URL}/agent/job/{job_id}"
    headers = {"X-API-Key": BANKR_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()


def wait_for_completion(job_id: str, timeout: int = 120) -> dict:
    """Wait for job to complete"""
    start = time.time()
    while time.time() - start < timeout:
        result = check_job(job_id)
        status = result.get("status", "pending")
        
        if status == "completed":
            return result
        elif status in ["failed", "cancelled"]:
            return result
        
        time.sleep(3)
    
    return {"status": "timeout", "error": "Job did not complete in time"}


def get_balance():
    """Get current portfolio balance"""
    result = submit_prompt("what is my portfolio balance?")
    job_id = result.get("jobId")
    if not job_id:
        return result
    
    completed = wait_for_completion(job_id)
    return completed


def execute_trade(action: str, token: str, amount: float) -> dict:
    """
    Execute a trade via Bankr
    
    Actions: buy, sell, swap
    """
    prompt = f"{action} {amount} {token}"
    
    if action.lower() == "buy":
        prompt = f"buy {amount} {token} using usd"
    elif action.lower() == "sell":
        prompt = f"sell {amount} {token} for usd"
    elif action.lower() == "swap":
        prompt = f"swap {amount} {token} for eth"
    
    print(f"Executing: {prompt}")
    result = submit_prompt(prompt)
    job_id = result.get("jobId")
    
    if not job_id:
        print(f"Error submitting: {result}")
        return result
    
    print(f"Job submitted: {job_id}")
    completed = wait_for_completion(job_id)
    
    return completed


def execute_strategy_signal(signal: dict) -> dict:
    """
    Execute a trade based on TradingView signal
    
    signal = {
        "direction": "long" | "short" | "neutral",
        "entry": 67000,
        "tp1": 68000,
        "tp2": 69000,
        "sl": 66000,
        "token": "BTC"
    }
    """
    direction = signal.get("direction", "neutral")
    token = signal.get("token", "BTC")
    entry = signal.get("entry")
    tp = signal.get("tp1")
    
    if direction == "neutral":
        return {"status": "skipped", "reason": "No signal"}
    
    # Calculate position size (risk 2% of portfolio)
    position_size = 0.01  # Default small amount for now
    
    if direction == "long":
        prompt = f"buy {position_size} {token} at market price"
    else:  # short
        prompt = f"open short position of {position_size} {token}"
    
    print(f"\n📡 Strategy Signal Received:")
    print(f"   Direction: {direction.upper()}")
    print(f"   Token: {token}")
    print(f"   Entry: ${entry:,.2f}")
    print(f"   TP: ${tp:,.2f}")
    print(f"   Executing: {prompt}")
    
    result = submit_prompt(prompt)
    job_id = result.get("jobId")
    
    if job_id:
        print(f"Job ID: {job_id}")
        completed = wait_for_completion(job_id)
        return completed
    
    return result


def generate_trading_report():
    """Generate a trading report from current market analysis"""
    prompt = """analyze the current crypto market and give me a brief report on:
    - BTC price and 24h movement
    - ETH price and 24h movement  
    - SOL price and 24h movement
    - any notable news or trends
    
    keep it concise, like a trader would write."""
    
    result = submit_prompt(prompt)
    job_id = result.get("jobId")
    
    if job_id:
        completed = wait_for_completion(job_id)
        return completed.get("response", "No response")
    
    return "Error generating report"


# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bankr Trading Bot")
    parser.add_argument("--action", choices=["buy", "sell", "swap", "balance", "report"], help="Trade action")
    parser.add_argument("--token", help="Token symbol (e.g., BTC, ETH, SOL)")
    parser.add_argument("--amount", type=float, help="Amount to trade")
    parser.add_argument("--signal", help="JSON signal from TradingView")
    parser.add_argument("--price", type=float, help="Entry price")
    parser.add_argument("--target", type=float, help="Target price")
    
    args = parser.parse_args()
    
    if args.action == "balance":
        print("Checking balance...")
        result = get_balance()
        print(json.dumps(result, indent=2))
    
    elif args.action == "report":
        print("Generating market report...")
        result = generate_trading_report()
        print(result)
    
    elif args.action in ["buy", "sell", "swap"]:
        if not args.token or not args.amount:
            print("Error: --token and --amount required")
            exit(1)
        
        result = execute_trade(args.action, args.token.upper(), args.amount)
        print(json.dumps(result, indent=2))
    
    elif args.signal:
        signal = json.loads(args.signal)
        result = execute_strategy_signal(signal)
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()
