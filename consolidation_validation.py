#!/usr/bin/env python3
"""
Consolidation Validation Test - Verify Phases 1-3 Still Pass
Quick validation after legacy path consolidation
"""

import asyncio
import aiohttp
import time
import psutil
import json
from datetime import datetime

async def validate_phase1():
    """Phase 1: System Prerequisites"""
    print("=== PHASE 1 VALIDATION: System Prerequisites ===")
    
    results = {
        "ollama_service": False,
        "api_connectivity": False,
        "hardware_detection": False,
        "models_available": 0
    }
    
    try:
        # Test Ollama connectivity
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    results["ollama_service"] = True
                    data = await response.json()
                    results["models_available"] = len(data.get("models", []))
                    print(f"✅ Ollama service: Running ({results['models_available']} models)")
                else:
                    print(f"❌ Ollama service: HTTP {response.status}")
    except Exception as e:
        print(f"❌ Ollama service: {e}")
    
    # Test router API connectivity
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11435/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    results["api_connectivity"] = True
                    print("✅ Router API: Connected")
                else:
                    print(f"❌ Router API: HTTP {response.status}")
    except Exception as e:
        print(f"❌ Router API: {e}")
    
    # Hardware detection
    try:
        memory_gb = psutil.virtual_memory().total / (1024**3)
        results["hardware_detection"] = memory_gb >= 16
        print(f"✅ Hardware: {memory_gb:.1f}GB RAM detected")
    except Exception as e:
        print(f"❌ Hardware detection: {e}")
    
    phase1_pass = all([
        results["ollama_service"],
        results["api_connectivity"], 
        results["hardware_detection"],
        results["models_available"] >= 8
    ])
    
    print(f"Phase 1 Status: {'✅ PASS' if phase1_pass else '❌ FAIL'}")
    return phase1_pass, results

async def validate_phase2():
    """Phase 2: Memory Management"""
    print("\n=== PHASE 2 VALIDATION: Memory Management ===")
    
    results = {
        "memory_detection": False,
        "model_selection": False,
        "memory_pressure_handling": False
    }
    
    try:
        # Test memory detection and model selection
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11435/api/team/status", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    system_info = data.get("system", {})
                    
                    available_memory = system_info.get("available_memory_gb", 0)
                    memory_pressure = system_info.get("memory_pressure", 100)
                    
                    results["memory_detection"] = available_memory > 0
                    results["memory_pressure_handling"] = memory_pressure < 90
                    
                    print(f"✅ Memory detection: {available_memory:.1f}GB available")
                    print(f"✅ Memory pressure: {memory_pressure:.1f}%")
                else:
                    print(f"❌ Status endpoint: HTTP {response.status}")
    except Exception as e:
        print(f"❌ Memory validation: {e}")
    
    # Test model selection (lightweight)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:11435/api/chat",
                json={"prompt": "Hello, quick test", "context": {}},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "response" in data and len(data["response"]) > 0:
                        results["model_selection"] = True
                        model_used = data.get("metadata", {}).get("member", "unknown")
                        print(f"✅ Model selection: {model_used} responded")
                    else:
                        print("❌ Model selection: Empty response")
                else:
                    print(f"❌ Model selection: HTTP {response.status}")
    except Exception as e:
        print(f"❌ Model selection: {e}")
    
    phase2_pass = all(results.values())
    print(f"Phase 2 Status: {'✅ PASS' if phase2_pass else '❌ FAIL'}")
    return phase2_pass, results

async def validate_phase3():
    """Phase 3: Tool Integration"""
    print("\n=== PHASE 3 VALIDATION: Tool Integration ===")
    
    results = {
        "team_members_endpoint": False,
        "mcp_server_import": False,
        "enhanced_capabilities": False
    }
    
    # Test team members endpoint
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11435/api/team/members", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    # API returns object with member IDs as keys, not array
                    members = data if isinstance(data, dict) else data.get("members", [])
                    member_count = len(members)
                    results["team_members_endpoint"] = member_count >= 8
                    print(f"✅ Team endpoint: {member_count} members available")
                else:
                    print(f"❌ Team endpoint: HTTP {response.status}")
    except Exception as e:
        print(f"❌ Team endpoint: {e}")
    
    # Test MCP server import (quick check)
    try:
        import sys
        sys.path.insert(0, '/Users/mcampos.cerda/Documents/Programming/ai-team-router/src')
        from mcp_server import MCPServer
        
        results["mcp_server_import"] = True
        print("✅ MCP server: Import successful")
    except Exception as e:
        print(f"❌ MCP server: Import failed - {e}")
    
    # Test enhanced chat with context
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:11435/api/chat",
                json={
                    "prompt": "Simple addition: 2+2=?", 
                    "context": {"priority": "normal", "temperature": 0.3}
                },
                timeout=aiohttp.ClientTimeout(total=20)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    metadata = data.get("metadata", {})
                    has_metadata = "member" in metadata and "elapsed_time" in metadata
                    results["enhanced_capabilities"] = has_metadata
                    print(f"✅ Enhanced chat: Response with metadata")
                else:
                    print(f"❌ Enhanced chat: HTTP {response.status}")
    except Exception as e:
        print(f"❌ Enhanced chat: {e}")
    
    phase3_pass = all(results.values())
    print(f"Phase 3 Status: {'✅ PASS' if phase3_pass else '❌ FAIL'}")
    return phase3_pass, results

async def main():
    """Run complete consolidation validation"""
    print("====================================================================")
    print("🔍 CONSOLIDATION VALIDATION TEST")
    print("====================================================================")
    print(f"Time: {datetime.now()}")
    print("Testing: Phases 1-3 still pass after legacy consolidation")
    print("")
    
    # Run all phase validations
    phase1_pass, phase1_results = await validate_phase1()
    phase2_pass, phase2_results = await validate_phase2()  
    phase3_pass, phase3_results = await validate_phase3()
    
    # Overall status
    all_phases_pass = phase1_pass and phase2_pass and phase3_pass
    
    print("\n" + "="*60)
    print("CONSOLIDATION VALIDATION SUMMARY")
    print("="*60)
    print(f"Phase 1 (System Prerequisites): {'✅ PASS' if phase1_pass else '❌ FAIL'}")
    print(f"Phase 2 (Memory Management): {'✅ PASS' if phase2_pass else '❌ FAIL'}")
    print(f"Phase 3 (Tool Integration): {'✅ PASS' if phase3_pass else '❌ FAIL'}")
    print("")
    print(f"Overall Status: {'✅ ALL PHASES PASS' if all_phases_pass else '❌ VALIDATION FAILED'}")
    
    if all_phases_pass:
        print("\n🎯 RESULT: Ready to proceed with Phase 4A")
        print("✅ Legacy consolidation did not break existing functionality")
        print("✅ Enhanced capabilities are working")
        print("✅ Rule 1 compliance maintained")
    else:
        print("\n⚠️ RESULT: Must fix issues before Phase 4A")
        print("❌ Some functionality broken by consolidation")
        print("❌ Rule 1 requires all phases to pass")
    
    # Save results
    validation_results = {
        "timestamp": datetime.now().isoformat(),
        "consolidation_validation": True,
        "phase1": {"pass": phase1_pass, "details": phase1_results},
        "phase2": {"pass": phase2_pass, "details": phase2_results}, 
        "phase3": {"pass": phase3_pass, "details": phase3_results},
        "overall_pass": all_phases_pass,
        "ready_for_phase4a": all_phases_pass
    }
    
    with open('validation_evidence/consolidation_validation.json', 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n📊 Results saved: validation_evidence/consolidation_validation.json")
    print("="*60)
    
    return all_phases_pass

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
