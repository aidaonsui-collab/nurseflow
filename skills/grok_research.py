#!/usr/bin/env python3
"""
Grok Research Tool
Uses xAI Grok API for autonomous research

Usage:
    python3 grok_research.py --query "latest sui news"
    
Or import and use:
    from grok_research import research
    result = research("What are the best trading strategies?")
"""

import os
import requests
from typing import Optional, Dict

# xAI Grok API
# Get your API key from https://console.x.ai/
# Note: May need to set up billing

XAI_API_KEY = os.environ.get("XAI_API_KEY", "")


def research(query: str, model: str = "grok-2-1212") -> Optional[str]:
    """
    Use Grok to research a query.
    
    Args:
        query: The research question
        model: Grok model to use (default: grok-2-1212)
        
    Returns:
        Research results as string
    """
    if not XAI_API_KEY:
        return "ERROR: XAI_API_KEY not set. Get key from https://console.x.ai/"
    
    url = "https://api.x.ai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """You are a research assistant. 
    Provide thorough, accurate information with sources when possible.
    Be concise but comprehensive. Format results clearly."""
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Exception: {e}"


def research_with_context(query: str, context: str) -> Optional[str]:
    """
    Research with additional context (e.g., for trading decisions)
    
    Args:
        query: Research question
        context: Additional context to consider
    """
    if not XAI_API_KEY:
        return "ERROR: XAI_API_KEY not set"
    
    url = "https://api.x.ai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    full_query = f"""Context: {context}

Question: {query}

Provide a thorough answer considering the context above."""

    data = {
        "model": "grok-2-1212",
        "messages": [{"role": "user", "content": full_query}],
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Exception: {e}"


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Grok Research Tool")
    parser.add_argument("--query", "-q", required=True, help="Research query")
    parser.add_argument("--context", "-c", help="Additional context")
    parser.add_argument("--model", "-m", default="grok-2-1212", help="Model to use")
    
    args = parser.parse_args()
    
    if args.context:
        result = research_with_context(args.query, args.context)
    else:
        result = research(args.query, args.model)
    
    print(result)
