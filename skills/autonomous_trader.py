#!/usr/bin/env python3
"""
Autonomous Trading Bot
Runs hourly, checks prices, executes trades based on strategy
"""
import os
import json
import time
import requests

BANKR_API_KEY = "bk_3GKNL8C5S6Z9WQEXVU6E43S92626PNZW"
API_URL = "https://api.bankr.bot"

# Strategy: Arcturus (bearish)
# Bias: 0/10 bearish
# Entry: $68,072-$68,465
# TP1: $67,680 | TP2: $66,870

STRATEGY = {
    "name": "Arcturus",
    "bias": "bearish",  # 0-10, 0=very bearish
    "short_entry_min": 68072,
    "short_entry_max": 68465,
    "tp1": 67680,
    "tp2": 66870,
    "min_collateral": 10,  # USDC
    "leverage": 10,
}

def submit_prompt(prompt):
    url = f"{API_URL}/agent/prompt"
    headers = {"X-API-Key": BANKR_API_KEY, "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"prompt": prompt}, timeout=30)
    return resp.json()

def check_job(job_id):
    url = f"{API_URL}/agent/job/{job_id}"
    headers = {"X-API-Key": BANKR_API_KEY}
    resp = requests.get(url, headers=headers, timeout=30)
    return resp.json()

def wait_for_completion(job_id, timeout=180):
    start = time.time()
    while time.time() - start < timeout:
        result = check_job(job_id)
        if result.get("status") == "completed":
            return result
        if result.get("status") in ["failed", "cancelled"]:
            return result
        time.sleep(10)
    return {"status": "timeout"}

def get_prices():
    """Get current BTC and SOL prices"""
    result = submit_prompt("what is the current price of BTC and SOL?")
    job_id = result.get("jobId")
    if not job_id:
        print("Error getting prices")
        return None
    
    completed = wait_for_completion(job_id)
    if completed.get("status") != "completed":
        print("Price check timeout")
        return None
    
    response = completed.get("response", "")
    return response

def get_balance():
    """Get current portfolio balance"""
    result = submit_prompt("show my full balance on all networks")
    job_id = result.get("jobId")
    if not job_id:
        return None
    
    completed = wait_for_completion(job_id)
    if completed.get("status") != "completed":
        return None
    
    return completed.get("response", "")

def parse_prices(text):
    """Parse BTC and SOL prices from response"""
    import re
    prices = {}
    
    # Match patterns like "$67,970" or "67,970.00"
    btc_match = re.search(r'btc.*?\$?([\d,]+)', text, re.IGNORECASE)
    sol_match = re.search(r'sol.*?\$?([\d,]+)', text, re.IGNORECASE)
    
    if btc_match:
        prices['BTC'] = float(btc_match.group(1).replace(',', ''))
    if sol_match:
        prices['SOL'] = float(sol_match.group(1).replace(',', ''))
    
    return prices

def should_trade(prices):
    """Determine if strategy conditions are met"""
    if not prices:
        return None, "No price data"
    
    btc = prices.get('BTC', 0)
    sol = prices.get('SOL', 0)
    
    # Bearish: looking for shorts
    # Short when price is in entry zone
    if btc > STRATEGY['short_entry_min'] and btc < STRATEGY['short_entry_max']:
        return "BTC", f"BTC ${btc} in short zone"
    
    if sol > STRATEGY['short_entry_min'] and sol < STRATEGY['short_entry_max']:
        return "SOL", f"SOL ${sol} in short zone"
    
    return None, f"Outside entry zone - BTC ${btc}, SOL ${sol}"

def open_position(token, collateral=10, leverage=10):
    """Open leveraged position"""
    prompt = f"open {leverage}x short on {token} with {collateral} usd collateral on avantis"
    print(f"Executing: {prompt}")
    
    result = submit_prompt(prompt)
    job_id = result.get("jobId")
    
    if not job_id:
        return {"status": "error", "message": "Failed to submit"}
    
    # Wait for completion
    completed = wait_for_completion(job_id, timeout=300)
    
    if completed.get("status") == "completed":
        response = completed.get("response", "")
        if "error" in response.lower() or "could not" in response.lower():
            return {"status": "failed", "message": response}
        return {"status": "success", "message": response}
    
    return {"status": "pending", "job_id": job_id}

def main():
    print("=" * 50)
    print("AUTONOMOUS TRADING BOT - Arcturus Strategy")
    print("=" * 50)
    
    # Get prices
    print("\n[1] Fetching prices...")
    price_text = get_prices()
    if not price_text:
        print("Failed to get prices")
        return
    
    prices = parse_prices(price_text)
    print(f"Prices: {prices}")
    
    # Check strategy
    print("\n[2] Checking strategy conditions...")
    token, reason = should_trade(prices)
    print(f"Signal: {token} - {reason}")
    
    # Get balance
    print("\n[3] Checking balance...")
    balance = get_balance()
    print(f"Balance: {balance[:200] if balance else 'Failed'}")
    
    # Decision
    if token:
        print(f"\n[4] TRADE SIGNAL: {token}")
        result = open_position(token, collateral=STRATEGY['min_collateral'], leverage=STRATEGY['leverage'])
        print(f"Result: {result}")
    else:
        print("\n[4] No trade - conditions not met")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
