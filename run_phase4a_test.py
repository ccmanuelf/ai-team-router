#!/usr/bin/env python3
"""
Phase 4A Validation Test - Collaborative Execution
Run this script in terminal to validate routing accuracy improvement
"""

import subprocess
import json
import time
import os
from datetime import datetime

def phase4a_validation_test():
    """Validate routing accuracy after memory management fixes"""
    print("="*60)
    print("PHASE 4A VALIDATION TEST")
    print("="*60)
    print("Testing routing accuracy after memory management fixes")
    print("Expected: 40% → 70%+ improvement")
    print("="*60)
    
    # Kill any existing router
    print("1. Stopping existing router...")
    subprocess.run(['pkill', '-f', 'ai_team_router.py'], capture_output=True)
    time.sleep(3)
    
    # Start router
    print("2. Starting router with fixes...")
    process = subprocess.Popen(['python3', 'src/ai_team_router.py'], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
    time.sleep(10)
    
    # Test cases for routing accuracy
    test_cases = [
        {
            "name": "Vue.js Component",
            "prompt": "Create a Vue.js component with reactive data",
            "expected_model": "DeepCoder",
            "category": "frontend"
        },
        {
            "name": "Excel VBA",
            "prompt": "Generate VBA code for Excel with 150k rows processing",
            "expected_model": "Qwen",
            "category": "data"
        },
        {
            "name": "Laravel API",
            "prompt": "Build a Laravel API endpoint with validation",
            "expected_model": "DeepSeek",
            "category": "backend"
        },
        {
            "name": "Simple Task",
            "prompt": "Hello world",
            "expected_model": "Any",
            "category": "simple"
        }
    ]
    
    results = []
    success_count = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test['name']}")
        print(f"   Prompt: {test['prompt']}")
        print(f"   Expected: {test['expected_model']}")
        
        try:
            # Make request with extended timeout
            result = subprocess.run([
                'curl', '-s', '-X', 'POST', '--max-time', '360',
                'http://localhost:11435/api/chat',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({"prompt": test["prompt"], "context": {}})
            ], capture_output=True, text=True, timeout=370)
            
            if result.returncode == 0 and result.stdout:
                try:
                    data = json.loads(result.stdout)
                    
                    if 'metadata' in data and 'error' not in data['metadata']:
                        model_used = data['metadata'].get('member', 'unknown')
                        model_id = data['metadata'].get('model', 'unknown')
                        response_time = data['metadata'].get('elapsed_time', 0)
                        response_preview = data.get('response', '')[:100] + "..."
                        
                        # Check routing correctness
                        routing_correct = False
                        if test['expected_model'] == "Any":
                            routing_correct = True
                        elif test['expected_model'] == "DeepCoder" and "DeepCoder" in model_used:
                            routing_correct = True
                        elif test['expected_model'] == "Qwen" and "Qwen" in model_used:
                            routing_correct = True
                        elif test['expected_model'] == "DeepSeek" and "DeepSeek" in model_used:
                            routing_correct = True
                        
                        print(f"   ✅ Model: {model_used}")
                        print(f"   ⏱️  Time: {response_time:.1f}s")
                        print(f"   🎯 Routing: {'✅ CORRECT' if routing_correct else '❌ WRONG'}")
                        
                        if routing_correct:
                            success_count += 1
                        
                        results.append({
                            "test": test['name'],
                            "category": test['category'],
                            "success": True,
                            "model_used": model_used,
                            "model_id": model_id,
                            "expected_model": test['expected_model'],
                            "routing_correct": routing_correct,
                            "response_time": response_time,
                            "response_preview": response_preview
                        })
                    else:
                        error_msg = data.get('metadata', {}).get('error', 'Unknown error')
                        print(f"   ❌ Error: {error_msg}")
                        results.append({
                            "test": test['name'],
                            "success": False,
                            "error": error_msg,
                            "routing_correct": False
                        })
                except json.JSONDecodeError:
                    print(f"   ❌ JSON decode error")
                    results.append({
                        "test": test['name'],
                        "success": False,
                        "error": "JSON decode error",
                        "routing_correct": False
                    })
            else:
                print(f"   ❌ HTTP error: {result.stderr}")
                results.append({
                    "test": test['name'],
                    "success": False,
                    "error": f"HTTP error: {result.stderr}",
                    "routing_correct": False
                })
        
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout (360s exceeded)")
            results.append({
                "test": test['name'],
                "success": False,
                "error": "Timeout",
                "routing_correct": False
            })
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                "test": test['name'],
                "success": False,
                "error": str(e),
                "routing_correct": False
            })
        
        # Delay between tests
        time.sleep(5)
    
    # Calculate metrics
    total_tests = len(test_cases)
    successful_tests = len([r for r in results if r.get('success', False)])
    correct_routing = success_count
    
    success_rate = (successful_tests / total_tests) * 100
    routing_accuracy = (correct_routing / total_tests) * 100
    
    print(f"\n{'='*60}")
    print("PHASE 4A RESULTS")
    print(f"{'='*60}")
    print(f"Total tests: {total_tests}")
    print(f"Successful responses: {successful_tests} ({success_rate:.1f}%)")
    print(f"Correct routing: {correct_routing} ({routing_accuracy:.1f}%)")
    
    # Baseline comparison
    baseline_accuracy = 40
    improvement = routing_accuracy - baseline_accuracy
    print(f"Improvement from baseline: +{improvement:.1f}% (was {baseline_accuracy}%)")
    
    # Target assessment
    target_accuracy = 70
    if routing_accuracy >= target_accuracy:
        print(f"🎯 TARGET ACHIEVED: ≥{target_accuracy}% routing accuracy")
        phase_passed = True
    else:
        print(f"❌ TARGET MISSED: Need ≥{target_accuracy}% routing accuracy")
        phase_passed = False
    
    # Save detailed results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "phase": "4A",
        "test_type": "routing_accuracy_validation",
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "correct_routing": correct_routing,
        "success_rate": success_rate,
        "routing_accuracy": routing_accuracy,
        "baseline_accuracy": baseline_accuracy,
        "improvement": improvement,
        "target_accuracy": target_accuracy,
        "phase_passed": phase_passed,
        "results": results
    }
    
    # Ensure validation_evidence directory exists
    os.makedirs('validation_evidence', exist_ok=True)
    
    with open('validation_evidence/phase4a_collaborative_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📊 Results saved: validation_evidence/phase4a_collaborative_results.json")
    print(f"📋 Router logs: logs/router.log")
    
    # Final status
    print(f"\n{'='*60}")
    if phase_passed:
        print("✅ PHASE 4A: PASSED")
        print("Ready to proceed to Phase 4B")
    else:
        print("❌ PHASE 4A: FAILED")
        print("Routing accuracy below target - investigate further")
    print(f"{'='*60}")
    
    # Cleanup
    print("\n5. Stopping router...")
    subprocess.run(['pkill', '-f', 'ai_team_router.py'], capture_output=True)
    
    return phase_passed

if __name__ == "__main__":
    try:
        success = phase4a_validation_test()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        subprocess.run(['pkill', '-f', 'ai_team_router.py'], capture_output=True)
        exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        subprocess.run(['pkill', '-f', 'ai_team_router.py'], capture_output=True)
        exit(1)
