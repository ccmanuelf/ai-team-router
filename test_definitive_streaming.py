#!/usr/bin/env python3
"""
Definitive Streaming vs Non-Streaming Comparison
Tests the exact same complex task with both methods
"""

import requests
import time
import json
from datetime import datetime

def test_streaming_vs_nonstreaming():
    """Definitive test: Same task, different methods"""
    print("="*60)
    print("🧪 DEFINITIVE TEST: STREAMING VS NON-STREAMING")
    print("="*60)
    
    # Use the task that timed out at 300s
    complex_task = {
        "name": "Complex Algorithm Implementation",
        "prompt": """Implement the following algorithms from scratch in Python with complete code:
1. Advanced sorting algorithms: QuickSort, MergeSort, HeapSort, RadixSort
2. Graph algorithms: Dijkstra, A*, Floyd-Warshall, Kruskal's MST
3. Dynamic programming: Longest Common Subsequence, Knapsack, Edit Distance
4. Machine learning: Linear Regression, K-Means, Decision Tree from scratch
5. Data structures: Red-Black Tree, B-Tree, Trie, Segment Tree
6. String algorithms: KMP, Rabin-Karp, Suffix Array
7. Numerical algorithms: FFT, Matrix multiplication, Prime factorization
8. Complete test suite for each algorithm
9. Performance benchmarking code
10. Visualization code for each algorithm
Include complete implementations with detailed comments and examples."""
    }
    
    print(f"🎯 Task: {complex_task['name']}")
    print(f"📝 Prompt length: {len(complex_task['prompt'])} chars")
    print("")
    
    results = {}
    
    # Test 1: Non-streaming 300s
    print("--- TEST 1: Non-streaming 300s ---")
    results["non_stream_300s"] = test_nonstreaming(complex_task, 300)
    
    # Test 2: Non-streaming 600s  
    print("\n--- TEST 2: Non-streaming 600s ---")
    results["non_stream_600s"] = test_nonstreaming(complex_task, 600)
    
    # Test 3: Streaming with 180s no-token timeout
    print("\n--- TEST 3: Streaming 180s no-token timeout ---")
    results["streaming_180s"] = test_streaming_smart(complex_task)
    
    # Analysis
    analyze_definitive_results(results)
    
    # Save results
    filename = f"definitive_streaming_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved: {filename}")
    return results

def test_nonstreaming(task, timeout_seconds):
    """Test non-streaming with specific timeout"""
    print(f"  ⏱️ Non-streaming test ({timeout_seconds}s timeout)...")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepcoder:latest",
                "prompt": task["prompt"],
                "stream": False
            },
            timeout=timeout_seconds
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")
            
            print(f"    ✅ SUCCESS: {elapsed:.1f}s")
            print(f"    📊 Response: {len(response_text)} chars")
            
            return {
                "success": True,
                "method": "non_streaming",
                "timeout_limit": timeout_seconds,
                "actual_time": elapsed,
                "response_length": len(response_text),
                "timed_out": False
            }
        else:
            print(f"    ❌ HTTP {response.status_code}")
            return {
                "success": False,
                "method": "non_streaming", 
                "timeout_limit": timeout_seconds,
                "error": f"HTTP {response.status_code}"
            }
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"    ⏰ TIMEOUT: {elapsed:.1f}s")
        return {
            "success": False,
            "method": "non_streaming",
            "timeout_limit": timeout_seconds,
            "actual_time": elapsed,
            "timed_out": True
        }
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"    ❌ ERROR: {e}")
        return {
            "success": False,
            "method": "non_streaming",
            "timeout_limit": timeout_seconds,
            "actual_time": elapsed,
            "error": str(e)
        }

def test_streaming_smart(task):
    """Test streaming with intelligent no-token timeout"""
    print(f"  🌊 Streaming test (180s no-token timeout)...")
    
    try:
        start_time = time.time()
        last_token_time = start_time
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepcoder:latest",
                "prompt": task["prompt"],
                "stream": True
            },
            stream=True,
            timeout=30  # Connection timeout only
        )
        
        if response.status_code != 200:
            print(f"    ❌ HTTP {response.status_code}")
            return {
                "success": False,
                "method": "streaming",
                "error": f"HTTP {response.status_code}"
            }
        
        # Stream processing with smart timeout
        full_response = ""
        chunk_count = 0
        no_token_timeout = 180  # 180s timeout for no new tokens
        total_timeout = 900  # 15 minute absolute maximum
        
        print(f"    📡 Streaming started...")
        
        for line in response.iter_lines():
            current_time = time.time()
            total_elapsed = current_time - start_time
            time_since_token = current_time - last_token_time
            
            # Absolute timeout check
            if total_elapsed > total_timeout:
                print(f"    ⏰ ABSOLUTE TIMEOUT: {total_elapsed:.1f}s")
                return {
                    "success": False,
                    "method": "streaming", 
                    "actual_time": total_elapsed,
                    "timeout_type": "absolute",
                    "chunks_received": chunk_count,
                    "response_length": len(full_response)
                }
            
            # No-token timeout check
            if time_since_token > no_token_timeout:
                print(f"    ⏰ NO-TOKEN TIMEOUT: {time_since_token:.1f}s since last token")
                return {
                    "success": False,
                    "method": "streaming",
                    "actual_time": total_elapsed,
                    "timeout_type": "no_token",
                    "chunks_received": chunk_count,
                    "response_length": len(full_response)
                }
            
            if line:
                last_token_time = current_time
                chunk_count += 1
                
                # Progress indicator
                if chunk_count % 500 == 0:
                    print(f"    📦 {chunk_count} chunks ({total_elapsed:.1f}s elapsed)")
                
                try:
                    chunk_data = json.loads(line)
                    if "response" in chunk_data:
                        full_response += chunk_data["response"]
                    
                    # Check if done
                    if chunk_data.get("done", False):
                        elapsed = current_time - start_time
                        print(f"    ✅ SUCCESS: {elapsed:.1f}s")
                        print(f"    📊 Response: {len(full_response)} chars")
                        print(f"    📦 Total chunks: {chunk_count}")
                        
                        return {
                            "success": True,
                            "method": "streaming",
                            "actual_time": elapsed,
                            "response_length": len(full_response),
                            "chunks": chunk_count,
                            "timed_out": False
                        }
                        
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON
        
        # Stream ended without done=True
        elapsed = time.time() - start_time
        print(f"    ⚠️ Stream ended unexpectedly: {elapsed:.1f}s")
        return {
            "success": False,
            "method": "streaming",
            "actual_time": elapsed,
            "chunks": chunk_count,
            "response_length": len(full_response),
            "error": "stream_ended_unexpectedly"
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"    ❌ ERROR: {e}")
        return {
            "success": False,
            "method": "streaming",
            "actual_time": elapsed,
            "error": str(e)
        }

def analyze_definitive_results(results):
    """Analyze the definitive comparison"""
    print(f"\n{'='*60}")
    print("DEFINITIVE STREAMING VS NON-STREAMING ANALYSIS")
    print("="*60)
    
    # Extract results
    ns_300 = results["non_stream_300s"]
    ns_600 = results["non_stream_600s"] 
    stream = results["streaming_180s"]
    
    print("📊 RESULTS SUMMARY:")
    print(f"  Non-streaming 300s: {'✅ SUCCESS' if ns_300.get('success') else '❌ FAILED'}")
    if ns_300.get("success"):
        print(f"    Time: {ns_300['actual_time']:.1f}s")
        print(f"    Response: {ns_300['response_length']} chars")
    elif ns_300.get("timed_out"):
        print(f"    Timed out at: {ns_300['actual_time']:.1f}s")
    
    print(f"  Non-streaming 600s: {'✅ SUCCESS' if ns_600.get('success') else '❌ FAILED'}")
    if ns_600.get("success"):
        print(f"    Time: {ns_600['actual_time']:.1f}s")
        print(f"    Response: {ns_600['response_length']} chars")
    elif ns_600.get("timed_out"):
        print(f"    Timed out at: {ns_600['actual_time']:.1f}s")
    
    print(f"  Streaming 180s no-token: {'✅ SUCCESS' if stream.get('success') else '❌ FAILED'}")
    if stream.get("success"):
        print(f"    Time: {stream['actual_time']:.1f}s")
        print(f"    Response: {stream['response_length']} chars")
        print(f"    Chunks: {stream['chunks']}")
    elif stream.get("timeout_type"):
        print(f"    Timeout type: {stream['timeout_type']}")
        print(f"    Time: {stream['actual_time']:.1f}s")
    
    # Strategic analysis
    print(f"\n🎯 STRATEGIC ANALYSIS:")
    
    if ns_300.get("timed_out") and ns_600.get("success"):
        print(f"  📈 Timeout increase (300s→600s) SOLVES the problem")
        print(f"  ⏱️ Actual completion time: {ns_600['actual_time']:.1f}s")
    
    if ns_300.get("timed_out") and stream.get("success"):
        print(f"  🌊 Streaming SOLVES the timeout problem")
        print(f"  ⚡ Streaming completion time: {stream['actual_time']:.1f}s")
    
    if ns_600.get("success") and stream.get("success"):
        time_diff = stream["actual_time"] - ns_600["actual_time"]
        if abs(time_diff) < 10:
            print(f"  ⚖️ Streaming and 600s timeout have SIMILAR performance")
        elif time_diff < 0:
            print(f"  🚀 Streaming is {abs(time_diff):.1f}s FASTER than non-streaming")
        else:
            print(f"  🐌 Streaming is {time_diff:.1f}s SLOWER than non-streaming")
    
    # Final recommendation
    print(f"\n🏆 RECOMMENDATION:")
    
    if ns_300.get("timed_out"):
        if stream.get("success") and ns_600.get("success"):
            # Both solutions work
            if stream["actual_time"] < ns_600["actual_time"] - 10:
                print(f"  ✅ IMPLEMENT STREAMING: Faster and more intelligent")
            else:
                print(f"  ✅ INCREASE TIMEOUT: Simpler solution, similar performance")
        elif stream.get("success") and not ns_600.get("success"):
            print(f"  ✅ IMPLEMENT STREAMING: Only solution that works")
        elif not stream.get("success") and ns_600.get("success"):
            print(f"  ✅ INCREASE TIMEOUT: Only solution that works")
        else:
            print(f"  ❌ BOTH SOLUTIONS FAILED: Need alternative approach")
    else:
        print(f"  🤔 NO TIMEOUT REPRODUCED: May be context-specific issue")

def main():
    """Run definitive streaming comparison"""
    print(f"Starting definitive test at {datetime.now()}")
    
    # Verify Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama not responding")
            return False
    except:
        print("❌ Ollama not running") 
        return False
    
    # Run test
    test_streaming_vs_nonstreaming()
    return True

if __name__ == "__main__":
    main()
