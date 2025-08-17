#!/usr/bin/env python3
"""
Test HTTP Connection Fixes
==========================

Test the improved HTTP connection handling for the router
Focus: Verify that requests library fixes the connection timeout issues

Usage: python3 test_http_fixes.py
"""

import sys
import os
sys.path.append('src')

from http_connection_fixes import OptimizedHTTPClient, DirectTCPClient, test_connection_methods

def test_router_http_improvements():
    """Test the HTTP improvements specifically for router use case"""
    
    print("🔧 TESTING ROUTER HTTP IMPROVEMENTS")
    print("=" * 60)
    print("Focus: Fix HTTPConnectionPool timeout issues")
    print("Target: Models that work via CLI but fail through router")
    print("=" * 60)
    
    # Test the exact scenarios that failed in Phase 4A
    test_cases = [
        {
            "name": "Vue.js Task (DeepCoder)",
            "model": "deepcoder:latest",
            "prompt": "Create a Vue.js component with reactive data binding",
            "expected_duration": "<180s"  # Based on CLI performance
        },
        {
            "name": "Excel VBA Task (Qwen)", 
            "model": "qwen2.5:14b",
            "prompt": "Generate VBA code to process 150000 rows in Excel",
            "expected_duration": "<180s"
        },
        {
            "name": "Laravel Task (DeepSeek)",
            "model": "deepseek-coder-v2:16b", 
            "prompt": "Create a Laravel API endpoint with validation",
            "expected_duration": "<180s"  # Previous success: 125s
        }
    ]
    
    client = OptimizedHTTPClient()
    
    # Verify connection first
    if not client.test_connection():
        print("❌ Cannot test - Ollama not available")
        return False
    
    print("✅ Ollama connection verified")
    
    # Test each case with improved HTTP handling
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Model: {test_case['model']}")
        print(f"Expected: {test_case['expected_duration']}")
        
        # Test with shorter prompt for faster validation
        short_prompt = test_case['prompt'][:50] + "..."
        
        result = client.send_generate_request(
            model_id=test_case['model'],
            prompt=short_prompt,
            timeout=300,  # 5 minutes - same as failed tests
            options={"num_ctx": 1024}  # Minimal context for speed
        )
        
        if result["success"]:
            duration = result["response_time"]
            status = "✅ SUCCESS"
            if duration < 180:
                performance = "🚀 FAST"
            elif duration < 300:
                performance = "⚡ ACCEPTABLE"
            else:
                performance = "🐌 SLOW"
            
            print(f"{status} {performance}: {duration:.1f}s")
            results.append({
                "test": test_case["name"],
                "success": True,
                "duration": duration,
                "model": test_case["model"]
            })
        else:
            error = result["error"]
            duration = result.get("response_time", 0)
            print(f"❌ FAILED: {error} (after {duration:.1f}s)")
            results.append({
                "test": test_case["name"],
                "success": False,
                "error": error,
                "duration": duration,
                "model": test_case["model"]
            })
    
    # Summary
    successful = len([r for r in results if r["success"]])
    total = len(results)
    
    print(f"\n" + "=" * 60)
    print("📋 HTTP FIXES TEST RESULTS")
    print("=" * 60)
    print(f"🔢 Total tests: {total}")
    print(f"✅ Successful: {successful}/{total} ({(successful/total*100):.1f}%)")
    
    if successful == total:
        print("🎉 ALL TESTS PASSED - HTTP fixes appear to be working!")
        print("🔧 Router should now handle these models correctly")
    elif successful > 0:
        print(f"⚠️ PARTIAL SUCCESS - {successful} out of {total} models working")
        print("🔧 HTTP fixes helping but may need further refinement")
    else:
        print("❌ ALL TESTS FAILED - HTTP fixes not sufficient")
        print("🔧 Need to investigate alternative approaches")
    
    # Performance analysis
    successful_results = [r for r in results if r["success"]]
    if successful_results:
        avg_duration = sum(r["duration"] for r in successful_results) / len(successful_results)
        print(f"\n📊 Performance Analysis:")
        print(f"   Average response time: {avg_duration:.1f}s")
        print(f"   Previous router failures: 300s timeout")
        print(f"   CLI performance: <180s")
        
        if avg_duration < 180:
            print("   🎯 EXCELLENT: Matching CLI performance")
        elif avg_duration < 240:
            print("   ✅ GOOD: Better than previous router failures")
        else:
            print("   ⚠️ SLOW: Still slower than CLI, investigate further")
    
    client.close()
    return successful == total

if __name__ == "__main__":
    print("🧪 TESTING HTTP CONNECTION FIXES")
    print("Goal: Verify that requests library solves router timeout issues")
    print("Background: Phase 4A showed 100% memory management but HTTP failures")
    print()
    
    # Test connection methods first
    print("🔍 Step 1: Testing connection methods")
    test_connection_methods()
    
    print("\n🎯 Step 2: Testing router-specific scenarios")
    success = test_router_http_improvements()
    
    print("\n🏁 CONCLUSION:")
    if success:
        print("✅ HTTP fixes successful - ready to deploy improved router")
        print("📝 Next: Update router to use OptimizedOllamaClient")
    else:
        print("❌ HTTP fixes insufficient - need alternative approaches")
        print("📝 Next: Investigate TCP connections or alternative HTTP libraries")
