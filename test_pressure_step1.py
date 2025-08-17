#!/usr/bin/env python3
"""
Test Memory Pressure Behavior - Confirm Health Monitor Issue
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

async def test_memory_pressure_routing():
    """Test what happens during high memory pressure"""
    print("="*60)
    print("MEMORY PRESSURE ROUTING TEST")
    print("="*60)
    
    # Test different types of requests that should use different models
    test_cases = [
        {"prompt": "Create a Vue.js component", "expected": "deepcoder", "type": "Vue coding"},
        {"prompt": "Generate VBA for Excel with 150k rows", "expected": "qwen", "type": "Excel VBA"},
        {"prompt": "Build Laravel API endpoint", "expected": "deepseek", "type": "Laravel PHP"},
        {"prompt": "Simple hello world", "expected": "any_small", "type": "Simple task"}
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['type']}")
        print(f"Prompt: {test_case['prompt']}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get system status first
                async with session.get("http://localhost:11435/api/team/status") as status_response:
                    if status_response.status == 200:
                        status_data = await status_response.json()
                        memory_pressure = status_data.get("system", {}).get("memory_pressure", 0)
                        available_memory = status_data.get("system", {}).get("available_memory_gb", 0)
                        print(f"Memory pressure: {memory_pressure:.1f}%")
                        print(f"Available memory: {available_memory:.2f}GB")
                
                # Make chat request
                start_time = time.time()
                async with session.post(
                    "http://localhost:11435/api/chat",
                    json={"prompt": test_case["prompt"], "context": {}},
                    timeout=aiohttp.ClientTimeout(total=45)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        elapsed = time.time() - start_time
                        
                        metadata = data.get("metadata", {})
                        model_used = metadata.get("member", "unknown")
                        model_id = metadata.get("model", "unknown")
                        
                        print(f"✅ Model used: {model_used}")
                        print(f"Model ID: {model_id}")
                        print(f"Response time: {elapsed:.1f}s")
                        
                        # Check if routing was correct
                        routing_correct = False
                        if test_case["expected"] == "deepcoder" and "deepcoder" in model_id.lower():
                            routing_correct = True
                        elif test_case["expected"] == "qwen" and "qwen" in model_id.lower():
                            routing_correct = True
                        elif test_case["expected"] == "deepseek" and "deepseek" in model_id.lower():
                            routing_correct = True
                        elif test_case["expected"] == "any_small" and any(x in model_id.lower() for x in ["gemma", "granite"]):
                            routing_correct = True
                        
                        result = {
                            "test_type": test_case["type"],
                            "prompt": test_case["prompt"],
                            "expected_model": test_case["expected"],
                            "actual_model": model_used,
                            "model_id": model_id,
                            "routing_correct": routing_correct,
                            "response_time": elapsed,
                            "memory_pressure": memory_pressure,
                            "available_memory": available_memory
                        }
                        
                        results.append(result)
                        print(f"Routing: {'✅ CORRECT' if routing_correct else '❌ INCORRECT'}")
                        
                    else:
                        print(f"❌ HTTP {response.status}")
                        
        except Exception as e:
            print(f"❌ Error: {e}")
            
        # Small delay between tests
        await asyncio.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("ROUTING ACCURACY SUMMARY")
    print("="*60)
    
    correct_routes = sum(1 for r in results if r["routing_correct"])
    total_routes = len(results)
    accuracy = (correct_routes / total_routes * 100) if total_routes > 0 else 0
    
    print(f"Correct routes: {correct_routes}/{total_routes}")
    print(f"Routing accuracy: {accuracy:.1f}%")
    
    # Check if all using tiny model (health monitor issue)
    tiny_model_count = sum(1 for r in results if "gemma" in r["model_id"].lower() and "1b" in r["model_id"])
    if tiny_model_count == total_routes:
        print("🚨 ALL REQUESTS USING GEMMA TINY - HEALTH MONITOR ISSUE CONFIRMED")
    elif tiny_model_count > 0:
        print(f"⚠️ {tiny_model_count}/{total_routes} requests forced to tiny model")
    
    # Check average memory pressure
    avg_pressure = sum(r["memory_pressure"] for r in results) / len(results) if results else 0
    print(f"Average memory pressure: {avg_pressure:.1f}%")
    
    if avg_pressure > 95:
        print("🚨 HIGH PRESSURE CONFIRMED - Health monitor bypassing normal routing")
    elif avg_pressure > 85:
        print("⚠️ MODERATE PRESSURE - Memory thresholds too aggressive")
    
    # Save results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "step": 1,
        "test_type": "memory_pressure_routing",
        "routing_accuracy": accuracy,
        "correct_routes": correct_routes,
        "total_routes": total_routes,
        "average_memory_pressure": avg_pressure,
        "all_using_tiny_model": tiny_model_count == total_routes,
        "results": results
    }
    
    with open('validation_evidence/step1_pressure_test.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📊 Results saved: validation_evidence/step1_pressure_test.json")
    return accuracy >= 70

if __name__ == "__main__":
    success = asyncio.run(test_memory_pressure_routing())
    exit(0 if success else 1)
