#!/usr/bin/env python3
"""
Debug Brave and DuckDuckGo specific issues
"""

import asyncio
import aiohttp
import json
import os

async def debug_brave_422():
    """Debug Brave 422 error"""
    print("🛡️ BRAVE 422 DEBUG")
    print("="*30)
    
    query = "Excel VBA functions"
    api_key = os.getenv("BRAVE_API_KEY")
    
    # Test with minimal parameters
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    
    # Try different parameter combinations
    test_params = [
        {"q": query, "count": 3},
        {"q": query, "count": 5},
        {"q": query},
        {"query": query, "count": 3}  # Wrong parameter name
    ]
    
    for i, params in enumerate(test_params, 1):
        print(f"\nTest {i}: {params}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    print(f"Status: {response.status}")
                    if response.status != 200:
                        text = await response.text()
                        print(f"Error: {text[:200]}")
                    else:
                        print("✅ Success")
                        break
        except Exception as e:
            print(f"Exception: {e}")

async def debug_duckduckgo_202():
    """Debug DuckDuckGo 202 error"""
    print(f"\n🦆 DUCKDUCKGO 202 DEBUG") 
    print("="*30)
    
    query = "Excel VBA functions"
    
    # 202 = Accepted (processing) - might need to wait
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"Status: {response.status}")
                text = await response.text()
                print(f"Response: {text[:500]}")
                
                if response.status == 202:
                    print("202 = Processing, DuckDuckGo might be rate limiting")
                elif response.status == 200:
                    try:
                        data = json.loads(text)
                        print(f"Keys: {list(data.keys())}")
                    except:
                        print("Not valid JSON")
    except Exception as e:
        print(f"Exception: {e}")

async def main():
    await debug_brave_422()
    await debug_duckduckgo_202()

if __name__ == "__main__":
    asyncio.run(main())
