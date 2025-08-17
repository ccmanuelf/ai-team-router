#!/usr/bin/env python3
"""
Comprehensive Phase 4A Test - After Step 1 & 2 Fixes
"""

import subprocess
import json
import time
import os
from datetime import datetime

def run_phase4a_after_fixes():
    """Run Phase 4A test with fixes applied"""
    print("="*60)
    print("PHASE 4A TEST - AFTER FIXES")
    print("="*60)
    
    os.chdir('/Users/mcampos.cerda/Documents/Programming/ai-team-router')
    
    # Ensure router is stopped
    subprocess.run(['pkill', '-f', 'ai_team_router.py'], capture_output=True)
    time.sleep(3)
    
    # Start router with fixes
    print("Starting router with Step 1 & 2 fixes...")
    process = subprocess.Popen(['python3', 'src/ai_team_router.py'], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
    time.sleep(10)  # Extra time for startup
    
    # Test cases from original Phase 4A
    test_cases = [
        {
            "name": "simple_coding",
            "prompt": "Write a Python function to sort a list",
            "expected_model": "mistral",
            "should_route_correctly": True
        },
        {
            "name": "vue_coding", 
            "prompt": "Create a Vue.js component with reactive data",
            "expected_model": "deepcoder",
            "should_route_correctly": True
        },
        {
            "name": "excel_vba",
            "prompt": "Generate VBA code for Excel inventory reconciliation with 150k rows",
            "expected_model": "qwen",
            "should_route_correctly": True
        },
        {
            "name": "laravel_php",
            "prompt": "Build a Laravel API endpoint with validation",
            "expected_model": "deepseek", 
            "should_route_correctly": True
        },
        {
            "name": "vision",
            "prompt": "Analyze this screenshot and extract text",
            "expected_model": "granite_vision",
            "should_route_correctly": True
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        
        try:
            start_time = time.time()
            result = subprocess.run([
                'curl', '-s', '-X', 'POST',
                'http://localhost:11435/api/chat',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({"prompt": test_case["prompt"], "context": {}})
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and result.stdout:
                try:
                    data = json.loads(result.stdout)
                    metadata = data.get('metadata', {})
                    
                    model_used = metadata.get('member', 'unknown')
                    model_id = metadata.get('model', 'unknown')
                    response_time = metadata.get('elapsed_time', time.time() - start_time)
                    
                    # Determine if routing was correct
                    routing_correct = False
                    expected = test_case['expected_model']
                    
                    if expected == "mistral" and "mistral" in model_id.lower():
                        routing_correct = True
                    elif expected == "deepcoder" and "deepcoder" in model_id.lower():
                        routing_correct = True
                    elif expected == "qwen" and "qwen" in model_id.lower():
                        routing_correct = True
                    elif expected == "deepseek" and "deepseek" in model_id.lower():
                        routing_correct = True
                    elif expected == "granite_vision" and "granite" in model_id.lower() and "vision" in model_id.lower():
                        routing_correct = True
                    
                    result_entry = {
                        "category": test_case["name"],
                        "success": True,
                        "response_time": response_time,
                        "model_used": model_used,
                        "model_id": model_id,
                        "expected_model": expected,
                        "routing_correct": routing_correct,
                        "response_length": len(data.get('response', '')),
                        "response_preview": data.get('response', '')[:100] + "..."
                    }
                    
                    print(f"✅ Success: {model_used}")
                    print(f"Routing: {'✅ CORRECT' if routing_correct else '❌ WRONG'}")
                    print(f"Time: {response_time:.1f}s")
                    
                except json.JSONDecodeError:
                    result_entry = {
                        "category": test_case["name"],
                        "success": False,
                        "error": "JSON decode error",
                        "routing_correct": False
                    }
                    print("❌ JSON decode error")
            else:
                result_entry = {
                    "category": test_case["name"], 
                    "success": False,
                    "error": f"HTTP error: {result.stderr}",
                    "routing_correct": False
                }
                print(f"❌ Request failed: {result.stderr}")
            
            results.append(result_entry)
            
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                "category": test_case["name"],
                "success": False,
                "error": str(e),
                "routing_correct": False
            })
        
        # Small delay between tests
        time.sleep(2)
    
    # Calculate metrics
    successful_tests = [r for r in results if r.get('success', False)]
    correct_routing = [r for r in results if r.get('routing_correct', False)]
    
    success_rate = (len(successful_tests) / len(results)) * 100
    routing_accuracy = (len(correct_routing) / len(results)) * 100
    
    avg_response_time = sum(r.get('response_time', 0) for r in successful_tests) / len(successful_tests) if successful_tests else 0
    
    print(f"\n{'='*60}")
    print("PHASE 4A RESULTS - AFTER FIXES")
    print(f"{'='*60}")
    print(f"Success rate: {success_rate:.1f}% ({len(successful_tests)}/{len(results)})")
    print(f"Routing accuracy: {routing_accuracy:.1f}% ({len(correct_routing)}/{len(results)})")
    print(f"Average response time: {avg_response_time:.1f}s")
    
    # Compare to baseline (40% routing accuracy)
    improvement = routing_accuracy - 40
    print(f"Improvement from baseline: +{improvement:.1f}%")
    
    if routing_accuracy >= 70:
        print("🎯 TARGET ACHIEVED: Routing accuracy ≥70%")
        target_met = True
    else:
        print("❌ TARGET MISSED: Need ≥70% routing accuracy")
        target_met = False
    
    # Save results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "phase": "4A_after_fixes",
        "success_rate": success_rate,
        "routing_accuracy": routing_accuracy,
        "avg_response_time": avg_response_time,
        "improvement_from_baseline": improvement,
        "target_met": target_met,
        "baseline_accuracy": 40,
        "target_accuracy": 70,
        "results": results
    }
    
    with open('validation_evidence/phase4a_after_fixes.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📊 Results saved: validation_evidence/phase4a_after_fixes.json")
    
    # Cleanup
    subprocess.run(['pkill', '-f', 'ai_team_router.py'], capture_output=True)
    
    return target_met

if __name__ == "__main__":
    success = run_phase4a_after_fixes()
    exit(0 if success else 1)
