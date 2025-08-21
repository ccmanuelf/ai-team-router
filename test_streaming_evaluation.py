#!/usr/bin/env python3
"""
Ollama Streaming Test - Isolated Evaluation
Tests streaming functionality for complex tasks with intelligent timeout
"""

import requests
import time
import json
from datetime import datetime

def test_ollama_streaming():
    """Test Ollama streaming API with intelligent timeout"""
    print("="*60)
    print("🧪 OLLAMA STREAMING TEST - ISOLATED EVALUATION")
    print("="*60)
    
    # Test cases: Simple vs Complex
    test_cases = [
        {
            "name": "Simple Math",
            "prompt": "What is 2+2?",
            "expected_time": "< 30s"
        },
        {
            "name": "Complex Python Processing", 
            "prompt": "Write and execute Python code to process a list of numbers: [1,2,3,4,5]. Calculate sum, average, create visualization, implement bubble sort, and provide detailed analysis with comments",
            "expected_time": "> 300s"
        },
        {
            "name": "Complex JavaScript Task",
            "prompt": "Write and execute JavaScript code to create a complete data processing pipeline: filter array of 1000 user objects, implement multiple sorting algorithms, create statistical analysis, and generate comprehensive report",
            "expected_time": "> 200s"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        
        # Test non-streaming first
        non_stream_result = test_non_streaming(test_case)
        
        # Test streaming 
        stream_result = test_streaming_with_timeout(test_case)
        
        # Compare results
        comparison = compare_results(non_stream_result, stream_result)
        
        results.append({
            "test": test_case["name"],
            "non_streaming": non_stream_result,
            "streaming": stream_result,
            "comparison": comparison
        })
    
    # Analysis
    analyze_streaming_benefits(results)
    
    return results

def test_non_streaming(test_case):
    """Test current non-streaming approach"""
    print(f"  📡 Non-streaming test...")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepcoder:latest",
                "prompt": test_case["prompt"],
                "stream": False
            },
            timeout=600  # 10 minutes max
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")
            
            print(f"    ✅ Completed in {elapsed:.1f}s")
            print(f"    📊 Response: {len(response_text)} chars")
            
            return {
                "success": True,
                "time": elapsed,
                "response_length": len(response_text),
                "timeout": False
            }
        else:
            print(f"    ❌ HTTP {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"    ⏰ Timeout after {elapsed:.1f}s")
        return {"success": False, "timeout": True, "time": elapsed}
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return {"success": False, "error": str(e)}

def test_streaming_with_timeout(test_case):
    """Test streaming with intelligent timeout"""
    print(f"  🌊 Streaming test...")
    
    try:
        start_time = time.time()
        last_data_time = start_time
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepcoder:latest", 
                "prompt": test_case["prompt"],
                "stream": True
            },
            stream=True,
            timeout=30  # Connection timeout
        )
        
        if response.status_code != 200:
            print(f"    ❌ HTTP {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
        
        # Process streaming response
        full_response = ""
        chunk_count = 0
        no_data_timeout = 60  # 60s timeout for no data
        
        for line in response.iter_lines():
            current_time = time.time()
            
            # Check for no-data timeout
            if current_time - last_data_time > no_data_timeout:
                elapsed = current_time - start_time
                print(f"    ⏰ No data timeout after {elapsed:.1f}s")
                return {
                    "success": False, 
                    "timeout": True, 
                    "time": elapsed,
                    "timeout_type": "no_data",
                    "chunks_received": chunk_count
                }
            
            if line:
                last_data_time = current_time
                chunk_count += 1
                
                try:
                    chunk_data = json.loads(line)
                    if "response" in chunk_data:
                        full_response += chunk_data["response"]
                    
                    # Check if done
                    if chunk_data.get("done", False):
                        elapsed = current_time - start_time
                        print(f"    ✅ Stream completed in {elapsed:.1f}s")
                        print(f"    📊 Response: {len(full_response)} chars")
                        print(f"    📦 Chunks: {chunk_count}")
                        
                        return {
                            "success": True,
                            "time": elapsed,
                            "response_length": len(full_response),
                            "chunks": chunk_count,
                            "timeout": False
                        }
                        
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON lines
        
        # If we exit loop without done=True
        elapsed = time.time() - start_time
        print(f"    ⚠️ Stream ended unexpectedly after {elapsed:.1f}s")
        return {
            "success": False,
            "time": elapsed,
            "chunks": chunk_count,
            "error": "stream_ended_unexpectedly"
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"    ❌ Error: {e}")
        return {"success": False, "error": str(e), "time": elapsed}

def compare_results(non_stream, stream):
    """Compare streaming vs non-streaming results"""
    comparison = {}
    
    if non_stream.get("success") and stream.get("success"):
        # Both successful - compare performance
        time_diff = stream["time"] - non_stream["time"]
        comparison["time_difference"] = time_diff
        comparison["streaming_faster"] = time_diff < 0
        comparison["both_successful"] = True
        
        # Compare response quality (length as proxy)
        length_diff = abs(stream["response_length"] - non_stream["response_length"])
        comparison["response_similar"] = length_diff < (non_stream["response_length"] * 0.1)  # Within 10%
        
    elif non_stream.get("timeout") and stream.get("success"):
        comparison["streaming_solved_timeout"] = True
        comparison["streaming_advantage"] = "Completed while non-streaming timed out"
        
    elif stream.get("timeout") and non_stream.get("success"):
        comparison["non_streaming_better"] = True
        comparison["streaming_disadvantage"] = "Timed out while non-streaming succeeded"
        
    else:
        comparison["both_failed"] = True
    
    return comparison

def analyze_streaming_benefits(results):
    """Analyze overall streaming benefits"""
    print(f"\n{'='*60}")
    print("STREAMING ANALYSIS RESULTS")
    print("="*60)
    
    successful_streams = sum(1 for r in results if r["streaming"].get("success", False))
    successful_non_streams = sum(1 for r in results if r["non_streaming"].get("success", False))
    
    print(f"Non-streaming success: {successful_non_streams}/{len(results)}")
    print(f"Streaming success: {successful_streams}/{len(results)}")
    
    # Analyze specific advantages
    timeout_fixes = sum(1 for r in results if r["comparison"].get("streaming_solved_timeout", False))
    performance_improvements = sum(1 for r in results if r["comparison"].get("streaming_faster", False))
    
    print(f"\nStreaming advantages:")
    print(f"  - Solved timeouts: {timeout_fixes} cases")
    print(f"  - Performance improvements: {performance_improvements} cases")
    
    # Recommendation
    if successful_streams > successful_non_streams:
        print(f"\n✅ RECOMMENDATION: Implement streaming")
        print(f"   Streaming shows clear advantages over non-streaming")
    elif timeout_fixes > 0:
        print(f"\n🤔 RECOMMENDATION: Consider streaming")
        print(f"   Streaming solves timeout issues but may have tradeoffs")
    else:
        print(f"\n❌ RECOMMENDATION: Keep non-streaming")
        print(f"   No clear advantage from streaming")
    
    return {
        "streaming_success_rate": successful_streams / len(results),
        "non_streaming_success_rate": successful_non_streams / len(results),
        "timeout_fixes": timeout_fixes,
        "performance_improvements": performance_improvements
    }

def main():
    """Run streaming evaluation"""
    print(f"Starting streaming evaluation at {datetime.now()}")
    
    # Verify Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama not responding")
            return False
    except:
        print("❌ Ollama not running")
        return False
    
    # Run tests
    results = test_ollama_streaming()
    
    # Save results
    filename = f"streaming_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved: {filename}")
    return True

if __name__ == "__main__":
    main()
