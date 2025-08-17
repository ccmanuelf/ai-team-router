#!/usr/bin/env python3
"""
Phase 4B Integration Test
========================

Test the integrated router with Phase 4A scenarios to validate 
that HTTP fixes work in the production router.

Goal: Achieve ≥70% routing accuracy with integrated OptimizedHTTPClient
"""

import sys
import os
import time
import json
import requests
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_phase4b_integration():
    """Test Phase 4B integrated router with Phase 4A scenarios"""
    
    print("🚀 PHASE 4B INTEGRATION TEST")
    print("=" * 60)
    print("Testing integrated router with proven HTTP fixes")
    print("Target: ≥70% routing accuracy")
    print("=" * 60)
    
    # Test scenarios from Phase 4A
    test_cases = [
        {
            "name": "Vue.js Component Task",
            "prompt": "Create a Vue.js component with reactive data binding for a todo list",
            "expected_domain": "coding",
            "expected_model_type": "DeepCoder"
        },
        {
            "name": "Excel VBA Processing", 
            "prompt": "Generate VBA code to process 150000 rows in Excel with data validation",
            "expected_domain": "enterprise", 
            "expected_model_type": "Qwen"
        },
        {
            "name": "Laravel API Development",
            "prompt": "Create a Laravel API endpoint with validation and database integration",
            "expected_domain": "coding",
            "expected_model_type": "DeepSeek"
        },
        {
            "name": "React Component Refactoring",
            "prompt": "Refactor this React component to use hooks and improve performance",
            "expected_domain": "coding", 
            "expected_model_type": "DeepCoder"
        },
        {
            "name": "Data Analysis Task",
            "prompt": "Analyze this dataset with pandas and create visualization",
            "expected_domain": "data",
            "expected_model_type": "Qwen"
        }
    ]
    
    # Check if router is running
    router_url = "http://localhost:11435"
    
    try:
        health_response = requests.get(f"{router_url}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            phase = health_data.get("phase", "unknown")
            if phase == "4B":
                print("✅ Phase 4B router detected and running")
            else:
                print(f"⚠️ Router running but phase is {phase}, not 4B")
                print("   Continuing with test...")
        else:
            print(f"❌ Router health check failed: {health_response.status_code}")
            return False, 0
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to router: {e}")
        print(f"💡 Start the Phase 4B router first:")
        print(f"   cd /Users/mcampos.cerda/Documents/Programming/ai-team-router")
        print(f"   python3 src/ai_team_router_phase4b.py")
        return False, 0
    
    print(f"🔗 Router URL: {router_url}")
    print(f"📊 Total test cases: {len(test_cases)}")
    print()
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 Test {i}: {test_case['name']}")
        print(f"Expected: {test_case['expected_model_type']} ({test_case['expected_domain']})")
        
        start_time = time.time()
        
        try:
            # Send request to integrated router
            response = requests.post(
                f"{router_url}/api/chat",
                json={
                    "prompt": test_case["prompt"],
                    "context": {}
                },
                timeout=900  # 15 minutes for large models
            )
            
            if response.status_code == 200:
                result_data = response.json()
                elapsed = time.time() - start_time
                
                # Extract metadata
                metadata = result_data.get("metadata", {})
                model_used = metadata.get("model", "unknown")
                member_name = metadata.get("member", "unknown")
                http_client = metadata.get("http_client", "unknown")
                phase = metadata.get("phase", "unknown")
                
                # Check if routing was correct
                routing_correct = False
                if test_case["expected_model_type"].lower() in member_name.lower():
                    routing_correct = True
                
                print(f"✅ SUCCESS: {elapsed:.1f}s")
                print(f"   Model: {member_name} ({model_used})")
                print(f"   HTTP Client: {http_client}")
                print(f"   Phase: {phase}")
                print(f"   Routing: {'✅ Correct' if routing_correct else '❌ Incorrect'}")
                
                if len(result_data.get("response", "")) > 50:
                    print(f"   Response: {result_data['response'][:100]}...")
                
                results.append({
                    "test": test_case["name"],
                    "success": True,
                    "routing_correct": routing_correct,
                    "model": model_used,
                    "member": member_name,
                    "duration": elapsed,
                    "http_client": http_client,
                    "phase": phase
                })
                
            else:
                elapsed = time.time() - start_time
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"   Duration: {elapsed:.1f}s")
                print(f"   Response: {response.text[:200]}...")
                
                results.append({
                    "test": test_case["name"],
                    "success": False,
                    "routing_correct": False,
                    "duration": elapsed,
                    "error": f"HTTP {response.status_code}"
                })
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            print(f"❌ TIMEOUT: {elapsed:.1f}s")
            
            results.append({
                "test": test_case["name"],
                "success": False,
                "routing_correct": False,
                "duration": elapsed,
                "error": "Timeout"
            })
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ ERROR: {e}")
            print(f"   Duration: {elapsed:.1f}s")
            
            results.append({
                "test": test_case["name"],
                "success": False,
                "routing_correct": False,
                "duration": elapsed,
                "error": str(e)
            })
        
        print()
    
    # Results analysis
    successful = len([r for r in results if r["success"]])
    correctly_routed = len([r for r in results if r["routing_correct"]])
    total = len(results)
    
    success_rate = (successful / total) * 100
    routing_accuracy = (correctly_routed / total) * 100
    
    print("=" * 60)
    print("📋 PHASE 4B INTEGRATION TEST RESULTS")
    print("=" * 60)
    print(f"🔢 Total tests: {total}")
    print(f"✅ Successful: {successful}/{total} ({success_rate:.1f}%)")
    print(f"🎯 Correct routing: {correctly_routed}/{total} ({routing_accuracy:.1f}%)")
    print(f"📊 Target: ≥70% routing accuracy")
    
    # Performance analysis
    successful_results = [r for r in results if r["success"]]
    if successful_results:
        avg_duration = sum(r["duration"] for r in successful_results) / len(successful_results)
        max_duration = max(r["duration"] for r in successful_results)
        min_duration = min(r["duration"] for r in successful_results)
        
        print(f"\n⚡ Performance Analysis:")
        print(f"   Average: {avg_duration:.1f}s")
        print(f"   Range: {min_duration:.1f}s - {max_duration:.1f}s")
        
        # Phase 4A baseline comparison
        phase4a_baseline = 52.5  # From Phase 4A results
        if avg_duration <= phase4a_baseline * 1.2:  # Within 20% of Phase 4A
            print(f"   🎯 EXCELLENT: Within 20% of Phase 4A baseline ({phase4a_baseline:.1f}s)")
        elif avg_duration <= phase4a_baseline * 1.5:  # Within 50% of Phase 4A
            print(f"   ✅ GOOD: Within 50% of Phase 4A baseline ({phase4a_baseline:.1f}s)")
        else:
            print(f"   ⚠️ SLOWER: Significantly slower than Phase 4A baseline ({phase4a_baseline:.1f}s)")
    
    # HTTP Client verification
    http_clients = set(r.get("http_client", "unknown") for r in successful_results)
    phases = set(r.get("phase", "unknown") for r in successful_results)
    
    print(f"\n🔧 Integration Verification:")
    print(f"   HTTP Clients: {', '.join(http_clients)}")
    print(f"   Phases: {', '.join(phases)}")
    
    if "OptimizedHTTPClient" in http_clients and "4B" in phases:
        print("   ✅ Phase 4B integration confirmed")
    else:
        print("   ⚠️ Phase 4B integration not detected")
    
    # Final conclusion
    print(f"\n🏁 FINAL CONCLUSION:")
    if routing_accuracy >= 70:
        print(f"✅ PHASE 4B SUCCESS: {routing_accuracy:.1f}% ≥ 70% target")
        print("🎉 HTTP fixes successfully integrated into production router")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"validation_evidence/phase4b_integration_{timestamp}.json"
        
        os.makedirs("validation_evidence", exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "phase": "4B",
                "total_tests": total,
                "successful": successful,
                "correctly_routed": correctly_routed,
                "success_rate": success_rate,
                "routing_accuracy": routing_accuracy,
                "target_met": routing_accuracy >= 70,
                "performance": {
                    "average_duration": avg_duration if successful_results else 0,
                    "min_duration": min_duration if successful_results else 0,
                    "max_duration": max_duration if successful_results else 0
                },
                "http_clients_used": list(http_clients),
                "phases_detected": list(phases),
                "detailed_results": results
            }, indent=2)
        
        print(f"📁 Results saved to: {results_file}")
        return True, routing_accuracy
        
    else:
        print(f"❌ PHASE 4B INCOMPLETE: {routing_accuracy:.1f}% < 70% target")
        print("🔧 HTTP integration needs further investigation")
        return False, routing_accuracy

def main():
    """Main test execution"""
    
    print("🧪 PHASE 4B INTEGRATION TEST")
    print("Testing router with integrated OptimizedHTTPClient")
    print()
    
    try:
        success, accuracy = test_phase4b_integration()
        
        if success:
            print(f"\n🎊 PHASE 4B COMPLETED SUCCESSFULLY!")
            print(f"📈 Routing accuracy: {accuracy:.1f}%")
            print(f"🚀 Router ready for production deployment")
            return True
        else:
            print(f"\n⚠️ PHASE 4B NEEDS ATTENTION")
            print(f"📉 Routing accuracy: {accuracy:.1f}% (target: 70%)")
            print(f"🔧 Review integration and investigate issues")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
