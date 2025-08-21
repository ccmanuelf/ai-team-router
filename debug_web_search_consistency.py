#!/usr/bin/env python3
"""
Debug Web Search Consistency Issue
Investigates why web search works randomly for same prompts
"""

import requests
import time
import json
from datetime import datetime

def test_web_search_consistency():
    """Test same prompt multiple times to identify inconsistency"""
    
    test_prompt = "Search for Excel VBA functions for processing large datasets and provide example"
    
    print("="*60)
    print("🔍 WEB SEARCH CONSISTENCY DEBUG")
    print("="*60)
    print(f"Prompt: {test_prompt}")
    print(f"Expected: Web search should be used consistently")
    print("")
    
    results = []
    
    for run in range(5):
        print(f"--- Run {run + 1}/5 ---")
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:11435/api/chat",
                json={"prompt": test_prompt},
                timeout=300
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                model_used = data.get("metadata", {}).get("model", "unknown")
                
                # Enhanced search detection
                search_indicators = [
                    "search", "found", "according to", "based on", 
                    "recent", "latest", "current", "2024", "2025",
                    "web", "online", "internet", "website", "source"
                ]
                
                has_search_content = any(indicator in response_text.lower() for indicator in search_indicators)
                
                # Look for specific web search artifacts
                web_artifacts = [
                    "https://", "http://", "www.", ".com", ".org",
                    "retrieved", "accessed", "via", "from the web"
                ]
                
                has_web_artifacts = any(artifact in response_text.lower() for artifact in web_artifacts)
                
                print(f"  Model: {model_used}")
                print(f"  Time: {elapsed:.1f}s")
                print(f"  Length: {len(response_text)} chars")
                print(f"  Search indicators: {'✅' if has_search_content else '❌'}")
                print(f"  Web artifacts: {'✅' if has_web_artifacts else '❌'}")
                print(f"  Preview: {response_text[:100]}...")
                
                results.append({
                    "run": run + 1,
                    "success": True,
                    "model": model_used,
                    "response_time": elapsed,
                    "response_length": len(response_text),
                    "has_search_indicators": has_search_content,
                    "has_web_artifacts": has_web_artifacts,
                    "response_preview": response_text[:200],
                    "full_response": response_text
                })
                
            else:
                print(f"  ❌ HTTP {response.status_code}")
                results.append({"run": run + 1, "success": False, "error": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({"run": run + 1, "success": False, "error": str(e)})
        
        # Wait between requests
        if run < 4:
            print("  Waiting 2s...")
            time.sleep(2)
    
    # Analysis
    print(f"\n{'='*60}")
    print("CONSISTENCY ANALYSIS")
    print("="*60)
    
    successful_runs = [r for r in results if r.get("success", False)]
    search_detected = [r for r in successful_runs if r.get("has_search_indicators", False)]
    web_artifacts = [r for r in successful_runs if r.get("has_web_artifacts", False)]
    
    print(f"Successful runs: {len(successful_runs)}/5")
    print(f"Search indicators: {len(search_detected)}/{len(successful_runs)}")
    print(f"Web artifacts: {len(web_artifacts)}/{len(successful_runs)}")
    print(f"Consistency rate: {len(search_detected)}/{len(successful_runs)} = {(len(search_detected)/max(1,len(successful_runs)))*100:.1f}%")
    
    if len(search_detected) != len(successful_runs):
        print(f"\n🚨 INCONSISTENCY DETECTED")
        print(f"Web search not used consistently!")
        
        # Show examples
        for r in successful_runs:
            status = "✅ SEARCH" if r.get("has_search_indicators") else "❌ NO SEARCH"
            print(f"  Run {r['run']}: {status} - {r['model']} ({r['response_time']:.1f}s)")
            print(f"    Preview: {r['response_preview']}...")
    else:
        print(f"\n✅ CONSISTENT BEHAVIOR")
        print(f"Web search used in all successful runs")
    
    # Save detailed evidence
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "web_search_consistency_debug",
        "prompt": test_prompt,
        "total_runs": 5,
        "successful_runs": len(successful_runs),
        "search_detected_count": len(search_detected),
        "consistency_rate": (len(search_detected)/max(1,len(successful_runs)))*100,
        "inconsistent": len(search_detected) != len(successful_runs),
        "detailed_results": results
    }
    
    filename = f"validation_evidence/web_search_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print(f"\n📊 Evidence saved: {filename}")
    
    return len(search_detected) == len(successful_runs)

def check_router_web_search_integration():
    """Check how router integrates web search"""
    print(f"\n{'='*60}")
    print("ROUTER WEB SEARCH INTEGRATION CHECK")
    print("="*60)
    
    # Check router status
    try:
        response = requests.get("http://localhost:11435/api/team/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print("✅ Router responding")
            print(f"  Active member: {status.get('active_member', 'None')}")
            print(f"  Available tools: {status.get('tools', [])}")
        else:
            print(f"❌ Router status error: {response.status_code}")
    except Exception as e:
        print(f"❌ Router connection error: {e}")
    
    # Check if web search is available as a tool
    # (This would require examining the router's tool configuration)
    
def main():
    """Run web search consistency debug"""
    print(f"Starting web search consistency debug at {datetime.now()}")
    
    # Test consistency
    is_consistent = test_web_search_consistency()
    
    # Check router integration
    check_router_web_search_integration()
    
    # Summary
    print(f"\n{'='*60}")
    print("DEBUG SUMMARY")
    print("="*60)
    
    if is_consistent:
        print("✅ Web search appears consistent")
        print("   Issue may be with test detection logic")
    else:
        print("🚨 Web search inconsistency CONFIRMED")
        print("   Same prompt produces different web search behavior")
        print("   This is a serious reliability issue")
    
    print("\nNext steps:")
    print("1. Examine router's web search tool integration")
    print("2. Check if models are ignoring web search tools")
    print("3. Investigate prompt interpretation differences")
    print("4. Consider forcing web search for specific keywords")

if __name__ == "__main__":
    main()
