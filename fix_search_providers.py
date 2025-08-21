#!/usr/bin/env python3
"""
Fix DuckDuckGo and Google CSE ID Issues
"""

import asyncio
import aiohttp
import os
import json
from datetime import datetime

async def debug_duckduckgo():
    """Debug DuckDuckGo API issue"""
    query = "Excel VBA functions for large datasets"
    
    print("🦆 DEBUGGING DUCKDUCKGO")
    print("="*40)
    
    # Test different DuckDuckGo endpoints
    endpoints = [
        f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1",
        f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1",
        f"https://api.duckduckgo.com/?q={query}&format=json"
    ]
    
    for i, url in enumerate(endpoints, 1):
        print(f"\nTest {i}: {url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    print(f"Status: {response.status}")
                    text = await response.text()
                    print(f"Response length: {len(text)} chars")
                    
                    if response.status == 200:
                        try:
                            data = json.loads(text)
                            print(f"JSON keys: {list(data.keys())}")
                            abstract = data.get("Abstract", "")
                            if abstract:
                                print(f"Abstract: {abstract[:100]}...")
                            else:
                                print("No Abstract found")
                        except json.JSONDecodeError:
                            print("Invalid JSON response")
                    else:
                        print(f"Error response: {text[:200]}")
                        
        except Exception as e:
            print(f"Exception: {e}")

async def fix_duckduckgo_implementation():
    """Create fixed DuckDuckGo function"""
    print(f"\n🔧 FIXED DUCKDUCKGO IMPLEMENTATION")
    print("="*40)
    
    # Alternative approach using instant answers
    query = "Excel VBA functions"
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Try multiple result sources
                    sources = [
                        ("Abstract", data.get("Abstract", "")),
                        ("Answer", data.get("Answer", "")),
                        ("Definition", data.get("Definition", "")),
                        ("RelatedTopics", data.get("RelatedTopics", []))
                    ]
                    
                    result = None
                    for source_name, source_data in sources:
                        if source_data:
                            if source_name == "RelatedTopics" and isinstance(source_data, list):
                                if source_data and "Text" in source_data[0]:
                                    result = f"DuckDuckGo ({source_name}): {source_data[0]['Text']}"
                                    break
                            else:
                                result = f"DuckDuckGo ({source_name}): {source_data}"
                                break
                    
                    if result:
                        print(f"✅ Fixed approach works: {result[:100]}...")
                        return True
                    else:
                        print("❌ No usable content found")
                        return False
                else:
                    print(f"❌ Status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_google_cse():
    """Check Google CSE configuration"""
    print(f"\n🔍 GOOGLE CSE CONFIGURATION")
    print("="*40)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    cx = os.getenv("GOOGLE_CX")
    
    print(f"GOOGLE_API_KEY: {'✅ SET' if api_key else '❌ MISSING'}")
    print(f"GOOGLE_CSE_ID: {'✅ SET' if cse_id else '❌ MISSING'}")
    print(f"GOOGLE_CX: {'✅ SET' if cx else '❌ MISSING'}")
    
    # The issue is using GOOGLE_CX instead of GOOGLE_CSE_ID
    if cx and not cse_id:
        print(f"\n🔧 ISSUE FOUND:")
        print(f"Code uses GOOGLE_CX but .env should have GOOGLE_CSE_ID")
        print(f"Solution: Update tools.py to use GOOGLE_CSE_ID")
        return "variable_mismatch"
    elif not cse_id and not cx:
        print(f"\n🔧 MISSING CSE ID:")
        print(f"Need to add GOOGLE_CSE_ID to .env file")
        return "missing_cse"
    else:
        print(f"\n✅ Configuration looks correct")
        return "ok"

async def main():
    """Debug and fix search provider issues"""
    print(f"Search Provider Fixes - {datetime.now()}")
    
    # Debug DuckDuckGo
    await debug_duckduckgo()
    
    # Test fixed implementation
    ddg_fixed = await fix_duckduckgo_implementation()
    
    # Check Google CSE
    google_issue = check_google_cse()
    
    # Summary
    print(f"\n{'='*50}")
    print("FIX SUMMARY")
    print("="*50)
    print(f"DuckDuckGo: {'✅ FIXABLE' if ddg_fixed else '❌ NEEDS INVESTIGATION'}")
    print(f"Google CSE: {google_issue}")
    
    if ddg_fixed:
        print(f"\nDuckDuckGo fix: Use multiple result sources")
    
    if google_issue == "variable_mismatch":
        print(f"Google fix: Update tools.py variable name")
    elif google_issue == "missing_cse":
        print(f"Google fix: Add GOOGLE_CSE_ID to environment")

if __name__ == "__main__":
    asyncio.run(main())
