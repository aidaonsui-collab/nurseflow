#!/usr/bin/env python3
"""
X/Twitter Posting Bot
Posts tweets using X API directly (not browser)

Usage:
    python3 x_poster.py --message "Your tweet here"
    
Or import and use:
    from x_poster import post_tweet
    post_tweet("Hello from the bot!")
"""

import os
import requests
from typing import Optional

# X Credentials (from ~/Documents/aida/aida.rtf)
CREDENTIALS = {
    "client_id": "Tmp1VnJGVDB0VTJraFpGU0tTRGQ6MTpjaQ",
    "client_secret": "IinYdzTb3A8Ff8qybSxwdpzaG0boRxlzKu1T4gokYfFcmdN7ax",
    "bearer_token": "AAAAAAAAAAAAAAAAAAAAALW7gEAAAAAGS1kFhvvYec3fUsYVgjgDNDJ6RU=ql12oCZeuTX0ILlx5gOhK6rMDbq299UIjjR44Dd3F2V7tDcn82",
    "consumer_key": "vAJYmP9jio4PZfdtfXLKYvUAB",
    "consumer_secret": "rnGvZMoCWjJIB4JmC4SSg50mBM8s4eMfQvpzaNfMWkpWuQvJC2",
    "access_token": "1869975779565621248-vgkerTSvLaR5pZEjrcg0tzYXkUp1EX",
    "token_secret": "zln6nj7O3mzDBNcBksAPFDCvaPHeH4ZZy4mJ50e2mZcE3"
}

# Note: X API Free tier does NOT allow posting tweets
# Only allows reading and some engagement
# Basic tier ($100/mo) required for posting

# Alternative: Use Selenium or Playwright for browser automation
# Or use the browser approach we have

def post_tweet(message: str) -> Optional[dict]:
    """
    Post a tweet using X API v2
    
    NOTE: Requires X API Basic tier ($100/month)
    Free tier cannot post tweets.
    """
    url = "https://api.twitter.com/2/tweets"
    
    headers = {
        "Authorization": f"Bearer {CREDENTIALS['bearer_token']}",
        "Content-Type": "application/json"
    }
    
    data = {"text": message}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None


def check_api_tier() -> str:
    """
    Check what API tier the account has
    """
    # Try to post a tweet to see if it works
    test_url = "https://api.twitter.com/2/tweets"
    
    headers = {
        "Authorization": f"Bearer {CREDENTIALS['bearer_token']}",
    }
    
    try:
        response = requests.get(test_url, headers=headers)
        return f"API Status: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="X Poster Bot")
    parser.add_argument("--message", "-m", required=True, help="Tweet message")
    parser.add_argument("--check", action="store_true", help="Check API tier")
    
    args = parser.parse_args()
    
    if args.check:
        print(check_api_tier())
    else:
        result = post_tweet(args.message)
        if result:
            print(f"Tweet posted! ID: {result.get('data', {}).get('id')}")
        else:
            print("Failed to post tweet. Note: X API Free tier cannot post.")
