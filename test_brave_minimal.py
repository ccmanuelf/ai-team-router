#!/usr/bin/env python3
"""
Test Brave API with different parameter combinations
"""
import asyncio
import aiohttp
import os

async def test_brave_params():
    api_key = os.getenv("BRAVE_API_KEY")
    url = "https://api.search.brave.com/res/v1/web/search"
    
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    
    # Test minimal request
    params = {"q": "test"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"Status: {response.status}")
            text = await response.text()
            print(f"Response: {text[:300]}")

if __name__ == "__main__":
    asyncio.run(test_brave_params())
