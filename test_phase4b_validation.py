#!/usr/bin/env python3
"""
Phase 4C Test with Phase 4B Router - Validation Test
"""

import subprocess
import time
import requests
import json
from datetime import datetime

def test_phase4b_router():
    """Test Phase 4B router functionality"""
    print("=== TESTING PHASE 4B ROUTER ===")
    
    # Kill any existing router
    subprocess.run(['pkill', '-f', 'ai_team_router'], capture_output=True)
    time.sleep(2)
    
    # Start Phase 4B router
    process = subprocess.Popen(['python3', 'src/ai_team_router_phase4b.py'], 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for startup
    for i in range(15):
        try:
            response = requests.get("http://localhost:11435/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Phase 4B router started ({i+1}s)")
                break
        except:
            time.sleep(1)
    else:
        print("❌ Phase 4B router failed to start")
        return False
    
    # Test sequence: Vue.js → Excel → Check memory
    tests = [
        {"name": "Vue.js", "prompt": "Create a Vue.js component", "expected_model": "deepcoder"},
        {"name": "Excel", "prompt": "Process 150k rows in Excel", "expected_model": "qwen"},
        {"name": "Simple", "prompt": "What is 2+2?", "expected_model": "any"}
    ]
    
    results = []
    
    for test in tests:
        try:
            # Get memory before
            status_before = requests.get("http://localhost:11435/api/team/status").json()
            mem_before = status_before["system"]["available_memory_gb"]
            
            # Make request
            start_time = time.time()
            response = requests.post("http://localhost:11435/api/chat", 
                                   json={"prompt": test["prompt"]}, timeout=90)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                model_used = data["metadata"]["model"]
                
                # Wait for cleanup
                time.sleep(12)  # Allow unload + 10s stabilization
                
                # Get memory after
                status_after = requests.get("http://localhost:11435/api/team/status").json()
                mem_after = status_after["system"]["available_memory_gb"]
                
                print(f"✅ {test['name']}: {model_used} ({elapsed:.1f}s)")
                print(f"   Memory: {mem_before:.1f}GB → {mem_after:.1f}GB")
                
                results.append({
                    "test": test["name"],
                    "success": True,
                    "model": model_used,
                    "time": elapsed,
                    "memory_before": mem_before,
                    "memory_after": mem_after,
                    "memory_recovered": mem_after > mem_before
                })
            else:
                print(f"❌ {test['name']}: HTTP {response.status_code}")
                results.append({"test": test["name"], "success": False})
                
        except Exception as e:
            print(f"❌ {test['name']}: {e}")
            results.append({"test": test["name"], "success": False, "error": str(e)})
    
    # Kill router
    process.terminate()
    
    # Analysis
    successful = sum(1 for r in results if r.get("success", False))
    memory_recovery = sum(1 for r in results if r.get("memory_recovered", False))
    
    print(f"\n=== RESULTS ===")
    print(f"Tests passed: {successful}/{len(tests)}")
    print(f"Memory recovery: {memory_recovery}/{len(results)} tests")
    
    # Save evidence
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "router_version": "phase4b",
        "tests_passed": successful,
        "total_tests": len(tests),
        "memory_recovery_rate": memory_recovery,
        "detailed_results": results
    }
    
    filename = f"validation_evidence/phase4b_router_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print(f"📊 Evidence saved: {filename}")
    
    return successful == len(tests) and memory_recovery >= 2

if __name__ == "__main__":
    success = test_phase4b_router()
    print(f"\nResult: {'✅ PHASE 4B FUNCTIONAL' if success else '❌ ISSUES FOUND'}")
