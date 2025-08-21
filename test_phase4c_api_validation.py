#!/usr/bin/env python3
"""
Phase 4C Test 1: MCP Server & API Endpoint Validation (Revised)
Tests router API endpoints and validates expected functionality
"""

import asyncio
import json
import subprocess
import sys
import time
import requests
from datetime import datetime

def test_router_startup():
    """Test 1.1: Router Startup"""
    print("=== TEST 1.1: Router Startup Check ===")
    
    try:
        response = requests.get("http://localhost:11435/health", timeout=5)
        if response.status_code == 200:
            print("✅ Router already running")
            return True, {"status": "already_running"}
        else:
            print("❌ Router responding but not healthy")
            return False, {"error": f"HTTP {response.status_code}"}
    except:
        print("⚠️ Router not running - attempting to start...")
        
        # Try to start router
        try:
            import os
            os.chdir('/Users/mcampos.cerda/Documents/Programming/ai-team-router')
            
            # Start router in background
            process = subprocess.Popen(['python3', 'src/ai_team_router.py'], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            # Wait for startup
            for i in range(30):  # 30 second timeout
                try:
                    response = requests.get("http://localhost:11435/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Router started successfully (took {i+1}s)")
                        return True, {"status": "started", "startup_time": i+1, "pid": process.pid}
                except:
                    time.sleep(1)
            
            print("❌ Router failed to start within 30s")
            process.terminate()
            return False, {"error": "startup_timeout"}
            
        except Exception as e:
            print(f"❌ Router startup failed: {e}")
            return False, {"error": str(e)}

def test_api_endpoints():
    """Test 1.2: API Endpoints"""
    print("\n=== TEST 1.2: API Endpoints ===")
    
    endpoints = [
        ("GET", "/health", "Health check"),
        ("GET", "/api/team/status", "Team status"),
        ("GET", "/api/team/members", "Team members"),
        ("GET", "/", "Root endpoint")
    ]
    
    results = {}
    
    for method, endpoint, description in endpoints:
        try:
            url = f"http://localhost:11435{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {description}: {response.status_code}")
                results[endpoint] = {"success": True, "status": response.status_code, "data_size": len(str(data))}
            else:
                print(f"❌ {description}: HTTP {response.status_code}")
                results[endpoint] = {"success": False, "status": response.status_code}
                
        except Exception as e:
            print(f"❌ {description}: {e}")
            results[endpoint] = {"success": False, "error": str(e)}
    
    successful = sum(1 for r in results.values() if r.get("success", False))
    return successful == len(endpoints), results

def test_chat_functionality():
    """Test 1.3: Chat Functionality"""
    print("\n=== TEST 1.3: Chat Functionality ===")
    
    test_cases = [
        {
            "name": "Simple Math",
            "prompt": "What is 2+2?",
            "context": {"temperature": 0.3}
        },
        {
            "name": "Vue.js Question", 
            "prompt": "How do I create a Vue.js component?",
            "context": {"priority": "normal"}
        },
        {
            "name": "Excel Question",
            "prompt": "How to process 150k rows in Excel?",
            "context": {"temperature": 0.7}
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:11435/api/chat",
                json={
                    "prompt": test_case["prompt"],
                    "context": test_case["context"]
                },
                timeout=300
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                metadata = data.get("metadata", {})
                model_used = metadata.get("model", "unknown")
                member_name = metadata.get("member", "unknown")
                
                print(f"✅ {test_case['name']}: {model_used} ({elapsed:.1f}s)")
                results[test_case["name"]] = {
                    "success": True,
                    "model_used": model_used,
                    "member_name": member_name,
                    "response_time": elapsed,
                    "response_length": len(response_text),
                    "has_response": len(response_text) > 0
                }
            else:
                print(f"❌ {test_case['name']}: HTTP {response.status_code}")
                results[test_case["name"]] = {"success": False, "status": response.status_code}
                
        except Exception as e:
            print(f"❌ {test_case['name']}: {e}")
            results[test_case["name"]] = {"success": False, "error": str(e)}
    
    successful = sum(1 for r in results.values() if r.get("success", False))
    return successful == len(test_cases), results

def test_team_status_details():
    """Test 1.4: Team Status Details"""
    print("\n=== TEST 1.4: Team Status Details ===")
    
    try:
        response = requests.get("http://localhost:11435/api/team/status", timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["active_member", "team_size", "system"]
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                print(f"❌ Missing fields: {missing}")
                return False, {"error": f"Missing fields: {missing}"}
            
            system = data.get("system", {})
            team_size = data.get("team_size", 0)
            memory_gb = system.get("total_memory_gb", 0)
            available_gb = system.get("available_memory_gb", 0)
            
            print(f"✅ Team size: {team_size}")
            print(f"✅ Total memory: {memory_gb:.1f}GB")
            print(f"✅ Available memory: {available_gb:.1f}GB")
            
            return True, {
                "team_size": team_size,
                "total_memory_gb": memory_gb,
                "available_memory_gb": available_gb,
                "has_all_fields": len(missing) == 0
            }
        else:
            print(f"❌ Status endpoint: HTTP {response.status_code}")
            return False, {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Status details test failed: {e}")
        return False, {"error": str(e)}

def test_team_members():
    """Test 1.5: Team Members"""
    print("\n=== TEST 1.5: Team Members ===")
    
    try:
        response = requests.get("http://localhost:11435/api/team/members", timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            # Check if we have members
            if isinstance(data, dict):
                member_count = len(data)
                
                # Check a few expected members
                expected_members = ["deepcoder_primary", "qwen_analyst", "granite_vision"]
                found_members = [m for m in expected_members if m in data]
                
                print(f"✅ Total members: {member_count}")
                print(f"✅ Expected members found: {len(found_members)}/{len(expected_members)}")
                
                # Check member structure
                first_member = next(iter(data.values())) if data else {}
                required_member_fields = ["name", "model_id", "memory_gb", "expertise"]
                member_fields_ok = all(f in first_member for f in required_member_fields)
                
                print(f"✅ Member structure: {'OK' if member_fields_ok else 'Missing fields'}")
                
                return True, {
                    "member_count": member_count,
                    "expected_found": len(found_members),
                    "structure_ok": member_fields_ok,
                    "members": list(data.keys())
                }
            else:
                print(f"❌ Unexpected data format: {type(data)}")
                return False, {"error": "unexpected_format"}
        else:
            print(f"❌ Members endpoint: HTTP {response.status_code}")
            return False, {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Team members test failed: {e}")
        return False, {"error": str(e)}

def main():
    """Run Phase 4C API Tests"""
    print("="*60)
    print("🧪 PHASE 4C - TEST 1: API ENDPOINT VALIDATION (REVISED)")
    print("="*60)
    print(f"Time: {datetime.now()}")
    print("")
    
    results = {}
    
    # Run tests
    test_results = [
        ("router_startup", test_router_startup()),
        ("api_endpoints", test_api_endpoints()),
        ("chat_functionality", test_chat_functionality()),
        ("team_status", test_team_status_details()),
        ("team_members", test_team_members())
    ]
    
    # Collect results
    passed_tests = 0
    for test_name, (success, data) in test_results:
        results[test_name] = {"success": success, "data": data}
        if success:
            passed_tests += 1
    
    # Summary
    total_tests = len(test_results)
    print(f"\n{'='*60}")
    print("API ENDPOINT VALIDATION SUMMARY")
    print("="*60)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    for test_name, (success, data) in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    overall_success = passed_tests == total_tests
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    # Save results
    test_evidence = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "api_endpoint_validation",
        "phase": "4C",
        "test_number": 1,
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "success_rate": (passed_tests/total_tests)*100,
        "overall_success": overall_success,
        "detailed_results": results
    }
    
    filename = f"validation_evidence/phase4c_test1_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(test_evidence, f, indent=2)
    
    print(f"\n📊 Results saved: {filename}")
    print("="*60)
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
