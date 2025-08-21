#!/usr/bin/env python3
"""
Search Tools Validation Script
Tests Tavily, Brave, DuckDuckGo, and Google search providers
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add src directory to path
sys.path.append('src')

try:
    from tools import execute_tool
except ImportError:
    print("❌ Cannot import tools.py")
    print("Run from project root directory")
    sys.exit(1)

async def test_search_provider(provider, query="Python pandas tutorial"):
    """Test a specific search provider"""
    print(f"\n--- Testing {provider.upper()} ---")
    
    try:
        start_time = datetime.now()
        result = await execute_tool("web_search", {
            "query": query,
            "provider": provider
        })
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if "error" in result.lower() or "failed" in result.lower():
            print(f"❌ {provider}: {result[:100]}...")
            return False, result
        else:
            print(f"✅ {provider}: {elapsed:.1f}s, {len(result)} chars")
            print(f"Preview: {result[:150]}...")
            return True, result
            
    except Exception as e:
        print(f"❌ {provider}: Exception - {e}")
        return False, str(e)

async def validate_all_providers():
    """Test all search providers"""
    print("="*60)
    print("🔍 SEARCH TOOLS VALIDATION")
    print("="*60)
    
    # Check environment variables
    print("Environment Check:")
    env_vars = {
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
        "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "GOOGLE_CSE_ID": os.getenv("GOOGLE_CSE_ID"),
        "SERPER_API_KEY": os.getenv("SERPER_API_KEY")
    }
    
    for var, value in env_vars.items():
        status = "✅ SET" if value else "❌ MISSING"
        print(f"  {var}: {status}")
    
    # Test providers
    providers = ["serper", "tavily", "brave", "google"]
    test_query = "Excel VBA functions for large datasets"
    
    results = {}
    working_providers = []
    
    for provider in providers:
        success, result = await test_search_provider(provider, test_query)
        results[provider] = {
            "success": success,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            working_providers.append(provider)
    
    # Summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print("="*60)
    print(f"Working providers: {len(working_providers)}/{len(providers)}")
    print(f"Success rate: {(len(working_providers)/len(providers))*100:.1f}%")
    
    for provider in providers:
        status = "✅ WORKING" if results[provider]["success"] else "❌ FAILED"
        print(f"  {provider}: {status}")
    
    if working_providers:
        print(f"\n🎯 Recommended provider: {working_providers[0]}")
    else:
        print(f"\n🚨 NO WORKING PROVIDERS - All search tools failed")
    
    # Save evidence
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "search_tools_validation",
        "environment": env_vars,
        "results": results,
        "working_providers": working_providers,
        "success_rate": (len(working_providers)/len(providers))*100
    }
    
    filename = f"validation_evidence/search_tools_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print(f"\n📊 Evidence saved: {filename}")
    
    return len(working_providers) > 0, working_providers

async def main():
    """Run search tools validation"""
    print(f"Search Tools Validation - {datetime.now()}")
    
    has_working_tools, working_providers = await validate_all_providers()
    
    if has_working_tools:
        print(f"\n✅ VALIDATION PASSED")
        print(f"Ready to integrate {len(working_providers)} working providers")
        print("Next: Integrate tools into router")
    else:
        print(f"\n❌ VALIDATION FAILED")
        print("Fix API keys/configuration before integration")
    
    return has_working_tools

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
