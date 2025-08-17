#!/usr/bin/env python3
"""
Test Step 1 Fix: Quick routing accuracy test
"""

import subprocess
import json
import time
import os
from datetime import datetime

def quick_routing_test():
    """Quick test of routing after Step 1 fix"""
    print("="*60)
    print("STEP 1 FIX TEST: Quick Routing Accuracy")
    print("="*60)
    
    os.chdir('/Users/mcampos.cerda/Documents/Programming/ai-team-router')
    
    # Kill any existing router
    subprocess.run(['pkill', '-f', 'ai_team_router.py'], capture_output=True)
    time.sleep(2)
    
    # Start router with fix
    print("Starting router with Step 1 fix...")
    process = subprocess.Popen(['python3', 'src/ai_team_router.py'], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
    time.sleep(8)  # Give more time to start
    
    # Test cases
    test_cases = [
        {"prompt": "Create a Vue.js component", "expected": "deepcoder", "name": "Vue.js"},
        {"prompt": "Generate VBA for Excel", "expected": "qwen", "name": "Excel VBA"}
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\nTesting {test['name']}...")
        try:
            result = subprocess.run([
                'curl', '-s', '-X', 'POST', 
                'http://localhost:11435/api/chat',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({"prompt": test["prompt"], "context": {}})
            ], capture_output=True, text=True, timeout=45)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                metadata = data.get('metadata', {})
                model_used = metadata.get('member', 'unknown')
                model_id = metadata.get('model', 'unknown')
                
                # Check correctness
                correct = False
                if test['expected'] == 'deepcoder' and 'deepcoder' in model_id.lower():
                    correct = True
                elif test['expected'] == 'qwen' and 'qwen' in model_id.lower():
                    correct = True
                
                results.append({
                    "test": test['name'],
                    "model_used": model_used,
                    "model_id": model_id,
                    "correct": correct
                })
                
                print(f"Model: {model_used}")
                print(f"Correct: {'✅' if correct else '❌'}")
            else:
                print(f"❌ Request failed: {result.stderr}")
                results.append({
                    "test": test['name'],
                    "model_used": "failed",
                    "model_id": "failed", 
                    "correct": False
                })
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Summary
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n{'='*60}")
    print("STEP 1 FIX RESULTS:")
    print(f"Routing accuracy: {accuracy:.1f}% ({correct_count}/{total_count})")
    
    if accuracy >= 50:
        print("✅ STEP 1 FIX SUCCESS - Routing improved")
        success = True
    else:
        print("❌ STEP 1 FIX FAILED - Routing still broken")
        success = False
    
    # Save results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "step": 1,
        "test_type": "routing_accuracy_after_fix",
        "accuracy": accuracy,
        "correct_routes": correct_count,
        "total_routes": total_count,
        "results": results
    }
    
    with open('validation_evidence/step1_fix_test.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"📊 Results saved: validation_evidence/step1_fix_test.json")
    return success

if __name__ == "__main__":
    success = quick_routing_test()
    exit(0 if success else 1)
