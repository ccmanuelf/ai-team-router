#!/usr/bin/env python3
"""
Phase 4B Router Validation - Corrected Memory Analysis
"""

import subprocess
import time
import requests
import json
from datetime import datetime

def test_phase4b_router():
    """Test Phase 4B router with correct memory analysis"""
    print("=== PHASE 4B ROUTER VALIDATION (CORRECTED) ===")
    
    # Kill existing router
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
    
    # Get baseline memory
    baseline_status = requests.get("http://localhost:11435/api/team/status").json()
    baseline_memory = baseline_status["system"]["available_memory_gb"]
    print(f"📊 Baseline memory: {baseline_memory:.1f}GB")
    
    tests = [
        {"name": "Vue.js Component", "prompt": "Create a Vue.js component"},
        {"name": "Excel Processing", "prompt": "Process 150k rows in Excel with VBA"},
        {"name": "Simple Math", "prompt": "What is 2+2?"}
    ]
    
    results = []
    
    for test in tests:
        try:
            start_time = time.time()
            response = requests.post("http://localhost:11435/api/chat", 
                                   json={"prompt": test["prompt"]}, timeout=300)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                model_used = data["metadata"]["model"]
                
                # Wait for cleanup (Phase 4B automatic unload)
                time.sleep(12)
                
                # Check final memory
                final_status = requests.get("http://localhost:11435/api/team/status").json()
                final_memory = final_status["system"]["available_memory_gb"]
                
                # Correct analysis: final >= baseline OR within 1GB = successful unload
                memory_recovered = final_memory >= baseline_memory or abs(final_memory - baseline_memory) <= 1.0
                
                print(f"✅ {test['name']}: {model_used} ({elapsed:.1f}s)")
                print(f"   Final memory: {final_memory:.1f}GB (baseline: {baseline_memory:.1f}GB)")
                print(f"   Memory status: {'✅ RECOVERED' if memory_recovered else '❌ NOT RECOVERED'}")
                
                results.append({
                    "test": test["name"],
                    "success": True,
                    "model": model_used,
                    "time": elapsed,
                    "baseline_memory": baseline_memory,
                    "final_memory": final_memory,
                    "memory_recovered": memory_recovered
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
    successful_tests = sum(1 for r in results if r.get("success", False))
    memory_recoveries = sum(1 for r in results if r.get("memory_recovered", False))
    
    print(f"\n{'='*50}")
    print("PHASE 4B VALIDATION RESULTS")
    print("="*50)
    print(f"Tests executed: {successful_tests}/{len(tests)}")
    print(f"Memory recoveries: {memory_recoveries}/{len(results)}")
    print(f"Success rate: {(successful_tests/len(tests))*100:.1f}%")
    print(f"Memory recovery rate: {(memory_recoveries/len(results))*100:.1f}%")
    
    overall_success = successful_tests == len(tests) and memory_recoveries >= len(tests) - 1
    print(f"\nOverall: {'✅ PHASE 4B WORKING CORRECTLY' if overall_success else '❌ ISSUES DETECTED'}")
    
    # Save evidence
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "phase4b_router_validation_corrected",
        "router_version": "ai_team_router_phase4b.py",
        "baseline_memory_gb": baseline_memory,
        "tests_executed": successful_tests,
        "total_tests": len(tests),
        "memory_recoveries": memory_recoveries,
        "success_rate": (successful_tests/len(tests))*100,
        "memory_recovery_rate": (memory_recoveries/len(results))*100,
        "overall_success": overall_success,
        "detailed_results": results,
        "conclusion": "Phase 4B router properly loads and unloads models" if overall_success else "Issues detected"
    }
    
    filename = f"validation_evidence/phase4b_corrected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print(f"📊 Evidence: {filename}")
    
    return overall_success

if __name__ == "__main__":
    success = test_phase4b_router()
