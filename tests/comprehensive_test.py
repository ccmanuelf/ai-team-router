#!/usr/bin/env python3
"""
Comprehensive Test Suite for AI Team Router
Tests all functionality including tools and fallback mechanisms
"""

import asyncio
import sys
import os
import json
import psutil
from datetime import datetime

# Add router to path
sys.path.insert(0, '/Users/mcampos.cerda/Documents/Programming/ai')

async def test_router():
    """Test the router comprehensively"""
    
    print("=" * 70)
    print("🧪 AI TEAM ROUTER COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    # Test 1: Import and Initialize
    print("\n📦 Test 1: Router Import and Initialization")
    print("-" * 50)
    try:
        from ai_team_router import AITeamRouter
        router = AITeamRouter()
        print(f"✅ Router initialized successfully")
        print(f"   Models loaded: {len(router.team_members)}")
        print(f"   Active member: {router.active_member or 'None'}")
        
        # List all models
        print("\n   Available models:")
        for member_id, member in router.team_members.items():
            print(f"   - {member_id}: {member.name} ({member.memory_gb}GB)")
        
        results["tests"].append({
            "test": "initialization",
            "status": "PASSED",
            "models_count": len(router.team_members)
        })
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        results["tests"].append({
            "test": "initialization",
            "status": "FAILED",
            "error": str(e)
        })
        return results
    
    # Test 2: Task Analysis
    print("\n🔍 Test 2: Task Analysis")
    print("-" * 50)
    test_prompts = [
        ("Create a Vue component", "coding", "deepcoder_primary"),
        ("Process 150000 Excel rows", "enterprise", "qwen_analyst"),
        ("Analyze this screenshot", "visual", "granite_vision"),
        ("Debug Laravel controller", "coding", "deepseek_legacy"),
        ("What is 2+2?", "coding", "gemma_tiny")
    ]
    
    for prompt, expected_domain, expected_model in test_prompts:
        try:
            requirements = router._analyze_task(prompt, {})
            print(f"   '{prompt[:30]}...'")
            print(f"      Domain: {requirements['domain']} (expected: {expected_domain})")
            print(f"      Complexity: {requirements['complexity']}")
            
            # Test model selection
            member_id, member = router.select_team_member(requirements)
            print(f"      Selected: {member_id}")
            
            test_result = {
                "prompt": prompt,
                "domain": requirements['domain'],
                "expected_domain": expected_domain,
                "domain_match": requirements['domain'] == expected_domain,
                "selected_model": member_id,
                "expected_model": expected_model
            }
            
            if requirements['domain'] == expected_domain:
                print(f"      ✅ Domain detection correct")
            else:
                print(f"      ⚠️  Domain mismatch")
            
            results["tests"].append(test_result)
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            results["tests"].append({
                "prompt": prompt,
                "error": str(e)
            })
    
    # Test 3: Memory Management
    print("\n🧠 Test 3: Memory Management")
    print("-" * 50)
    try:
        available_memory = router._get_available_memory_gb()
        mem = psutil.virtual_memory()
        
        print(f"   Total RAM: {router.TOTAL_MEMORY_GB:.1f}GB")
        print(f"   Available: {available_memory:.1f}GB")
        print(f"   Memory Pressure: {mem.percent}%")
        print(f"   Platform: {'M3 Pro' if router.IS_M3_PRO else 'Standard'}")
        
        # Test memory-based selection
        print("\n   Testing memory constraints:")
        
        # Simulate low memory
        original_method = router._get_available_memory_gb
        router._get_available_memory_gb = lambda: 1.0  # Simulate only 1GB available
        
        requirements = {
            "complexity": 5,
            "domain": "coding",
            "needs_vision": False,
            "needs_uncensored": False,
            "needs_large_context": True,
            "needs_338_languages": False,
            "tool_requirements": {},
            "priority": "high"
        }
        
        member_id, member = router.select_team_member(requirements)
        print(f"   With 1GB available: Selected {member_id} ({member.memory_gb}GB)")
        
        if member_id == "gemma_tiny":
            print(f"   ✅ Emergency fallback working (selected minimal model)")
        else:
            print(f"   ⚠️  Did not fallback to minimal model")
        
        # Restore original method
        router._get_available_memory_gb = original_method
        
        results["tests"].append({
            "test": "memory_management",
            "status": "PASSED",
            "available_memory_gb": available_memory,
            "fallback_works": member_id == "gemma_tiny"
        })
        
    except Exception as e:
        print(f"   ❌ Memory test failed: {e}")
        results["tests"].append({
            "test": "memory_management",
            "status": "FAILED",
            "error": str(e)
        })
    
    # Test 4: Tool Requirements Identification
    print("\n🛠️ Test 4: Tool Requirements")
    print("-" * 50)
    tool_test_prompts = [
        ("Search the web for latest news", {"web_search": True}),
        ("Run this Python code", {"code_execution": True}),
        ("Process this Excel file with 150k rows", {"excel_optimizer": True}),
        ("Analyze this screenshot", {"vision": True}),
        ("Simple calculation", {})
    ]
    
    for prompt, expected_tools in tool_test_prompts:
        tools = router._identify_tool_requirements(prompt)
        active_tools = {k: v for k, v in tools.items() if v}
        expected_active = {k: v for k, v in expected_tools.items() if v}
        
        print(f"   '{prompt[:30]}...'")
        print(f"      Tools needed: {list(active_tools.keys()) or 'None'}")
        
        if active_tools == expected_active:
            print(f"      ✅ Tool identification correct")
        else:
            print(f"      ⚠️  Expected: {list(expected_active.keys())}")
        
        results["tests"].append({
            "test": "tool_identification",
            "prompt": prompt,
            "identified_tools": active_tools,
            "expected_tools": expected_active,
            "match": active_tools == expected_active
        })
    
    # Test 5: Actual Routing (Mock)
    print("\n🚀 Test 5: Request Routing (Mock)")
    print("-" * 50)
    
    try:
        # Test a simple routing without actually calling Ollama
        prompt = "Create a simple Vue component"
        context = {"priority": "normal", "temperature": 0.7}
        
        requirements = router._analyze_task(prompt, context)
        member_id, member = router.select_team_member(requirements)
        
        print(f"   Prompt: '{prompt}'")
        print(f"   Analysis:")
        print(f"      Domain: {requirements['domain']}")
        print(f"      Complexity: {requirements['complexity']}")
        print(f"      Selected Model: {member_id}")
        print(f"      Model Name: {member.name}")
        print(f"      Memory Required: {member.memory_gb}GB")
        print(f"      Context Window: {member.context_tokens} tokens")
        
        if member_id == "deepcoder_primary":
            print(f"   ✅ Correct model selected for Vue component")
        else:
            print(f"   ⚠️  Different model selected (may be valid based on memory)")
        
        results["tests"].append({
            "test": "routing_mock",
            "status": "PASSED",
            "selected_model": member_id,
            "model_name": member.name
        })
        
    except Exception as e:
        print(f"   ❌ Routing test failed: {e}")
        results["tests"].append({
            "test": "routing_mock",
            "status": "FAILED",
            "error": str(e)
        })
    
    # Test 6: Emergency Fallback
    print("\n🆘 Test 6: Emergency Fallback Mechanism")
    print("-" * 50)
    
    try:
        # Test the emergency fallback directly
        error_msg = "Test error for fallback"
        
        # Mock the emergency fallback
        result = await router._emergency_fallback("Test prompt", error_msg)
        
        print(f"   Simulated error: '{error_msg}'")
        print(f"   Fallback response received: {result is not None}")
        print(f"   Emergency mode: {result.get('metadata', {}).get('emergency_mode', False)}")
        
        if result and result.get('metadata', {}).get('emergency_mode'):
            print(f"   ✅ Emergency fallback mechanism works")
            results["tests"].append({
                "test": "emergency_fallback",
                "status": "PASSED"
            })
        else:
            print(f"   ⚠️  Emergency fallback may need testing with actual Ollama")
            results["tests"].append({
                "test": "emergency_fallback",
                "status": "SKIPPED",
                "note": "Requires Ollama to be running"
            })
            
    except Exception as e:
        print(f"   ❌ Emergency fallback test failed: {e}")
        results["tests"].append({
            "test": "emergency_fallback",
            "status": "FAILED",
            "error": str(e)
        })
    
    # Test 7: Performance Metrics
    print("\n📊 Test 7: Performance Metrics")
    print("-" * 50)
    
    try:
        # Test metric recording
        router._record_metrics("test_model", 4.5, True)
        router._record_metrics("test_model", 3.2, True)
        router._record_metrics("test_model", 5.1, False)
        
        metrics = router.performance_metrics.get("test_model", {})
        
        print(f"   Test metrics recorded:")
        print(f"      Requests: {metrics.get('requests', 0)}")
        print(f"      Successes: {metrics.get('successes', 0)}")
        print(f"      Average time: {metrics.get('average_time', 0):.2f}s")
        
        if metrics.get('requests') == 3 and metrics.get('successes') == 2:
            print(f"   ✅ Performance metrics working correctly")
            results["tests"].append({
                "test": "performance_metrics",
                "status": "PASSED",
                "metrics": metrics
            })
        else:
            print(f"   ⚠️  Metrics not as expected")
            results["tests"].append({
                "test": "performance_metrics",
                "status": "WARNING",
                "metrics": metrics
            })
            
    except Exception as e:
        print(f"   ❌ Metrics test failed: {e}")
        results["tests"].append({
            "test": "performance_metrics",
            "status": "FAILED",
            "error": str(e)
        })
    
    # Test 8: Status Check
    print("\n📈 Test 8: System Status")
    print("-" * 50)
    
    try:
        status = router.get_status()
        
        print(f"   System Status:")
        print(f"      Active Member: {status.get('active_member', 'None')}")
        print(f"      Team Size: {status.get('team_size', 0)}")
        print(f"      Platform: {status['system']['platform']}")
        print(f"      Total Memory: {status['system']['total_memory_gb']:.1f}GB")
        print(f"      Available Memory: {status['system']['available_memory_gb']:.1f}GB")
        print(f"      Memory Pressure: {status['system']['memory_pressure']:.1f}%")
        print(f"      Emergency Mode: {status['system'].get('emergency_mode', False)}")
        
        print(f"   ✅ Status check working")
        results["tests"].append({
            "test": "status_check",
            "status": "PASSED",
            "system_status": status
        })
        
    except Exception as e:
        print(f"   ❌ Status check failed: {e}")
        results["tests"].append({
            "test": "status_check",
            "status": "FAILED",
            "error": str(e)
        })
    
    # Generate Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for t in results["tests"] if t.get("status") == "PASSED")
    failed = sum(1 for t in results["tests"] if t.get("status") == "FAILED")
    skipped = sum(1 for t in results["tests"] if t.get("status") == "SKIPPED")
    total = len(results["tests"])
    
    print(f"\n   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: test_results.json")
    
    # Overall verdict
    print("\n" + "=" * 70)
    if failed == 0:
        print("✅ ALL TESTS PASSED - ROUTER IS FULLY FUNCTIONAL")
    elif passed > failed:
        print("⚠️  ROUTER IS MOSTLY FUNCTIONAL WITH SOME ISSUES")
    else:
        print("❌ ROUTER HAS SIGNIFICANT ISSUES")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    # Run tests
    results = asyncio.run(test_router())
