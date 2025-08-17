#!/usr/bin/env python3
"""
Step 1: Verify Memory Timeout Configuration
"""

import re
import json
import sys
from datetime import datetime

def analyze_unload_function():
    """Analyze the _unload_model function for timeout settings"""
    with open('src/ai_team_router.py', 'r') as f:
        content = f.read()
    
    # Extract _unload_model function
    unload_start = content.find('async def _unload_model(self, model_id):')
    if unload_start == -1:
        return {"error": "_unload_model function not found"}
    
    # Find function end (next async def or class)
    next_func = content.find('async def', unload_start + 1)
    next_class = content.find('def _force_context_reset', unload_start + 1)
    unload_end = min(x for x in [next_func, next_class] if x > unload_start)
    
    unload_function = content[unload_start:unload_end]
    
    # Extract timeout value
    timeout_match = re.search(r'max_wait_time\s*=\s*([\d.]+)', unload_function)
    timeout_value = float(timeout_match.group(1)) if timeout_match else None
    
    # Extract target release
    target_match = re.search(r'target_release_gb\s*=\s*([\d.]+)', unload_function)
    target_value = float(target_match.group(1)) if target_match else None
    
    # Check interval
    interval_match = re.search(r'check_interval\s*=\s*([\d.]+)', unload_function)
    interval_value = float(interval_match.group(1)) if interval_match else None
    
    return {
        "timeout_seconds": timeout_value,
        "target_release_gb": target_value, 
        "check_interval_seconds": interval_value,
        "function_length": len(unload_function.split('\n'))
    }

def analyze_route_request():
    """Analyze route_request for single model enforcement"""
    with open('src/ai_team_router.py', 'r') as f:
        content = f.read()
    
    # Find route_request function
    route_start = content.find('async def route_request(self, prompt, context=None):')
    if route_start == -1:
        return {"error": "route_request function not found"}
    
    # Find function end
    next_func = content.find('def get_status(self):', route_start)
    route_function = content[route_start:next_func]
    
    # Check for unload logic
    has_unload_check = 'self.active_member and self.active_member != member_id' in route_function
    unload_call = '_unload_model' in route_function
    
    # Check if unload is in else block (problem)
    unload_in_else = False
    lines = route_function.split('\n')
    in_else_block = False
    unload_line = -1
    
    for i, line in enumerate(lines):
        if 'else:' in line and 'health_issue' in lines[i-1] if i > 0 else False:
            in_else_block = True
        elif line.strip().startswith('self.active_member = member_id'):
            in_else_block = False
        elif '_unload_model' in line and in_else_block:
            unload_in_else = True
            unload_line = i
    
    return {
        "has_unload_check": has_unload_check,
        "has_unload_call": unload_call,
        "unload_in_else_block": unload_in_else,
        "unload_line_position": unload_line
    }

def main():
    print("="*60)
    print("STEP 1: MEMORY TIMEOUT VERIFICATION")
    print("="*60)
    
    # Analyze unload function
    unload_analysis = analyze_unload_function()
    print("\n📋 UNLOAD FUNCTION ANALYSIS:")
    if "error" in unload_analysis:
        print(f"❌ {unload_analysis['error']}")
        return False
    
    print(f"✅ Timeout: {unload_analysis['timeout_seconds']}s")
    print(f"✅ Target release: {unload_analysis['target_release_gb']}GB")
    print(f"✅ Check interval: {unload_analysis['check_interval_seconds']}s")
    print(f"✅ Function size: {unload_analysis['function_length']} lines")
    
    timeout_ok = unload_analysis['timeout_seconds'] == 10.0
    target_ok = unload_analysis['target_release_gb'] == 0.5
    
    print(f"\n🎯 TIMEOUT STATUS: {'✅ CORRECT (10s)' if timeout_ok else '❌ INCORRECT'}")
    
    # Analyze route request
    route_analysis = analyze_route_request()
    print("\n📋 ROUTE REQUEST ANALYSIS:")
    if "error" in route_analysis:
        print(f"❌ {route_analysis['error']}")
        return False
    
    print(f"{'✅' if route_analysis['has_unload_check'] else '❌'} Has unload check: {route_analysis['has_unload_check']}")
    print(f"{'✅' if route_analysis['has_unload_call'] else '❌'} Has unload call: {route_analysis['has_unload_call']}")
    print(f"{'❌' if route_analysis['unload_in_else_block'] else '✅'} Unload in else block: {route_analysis['unload_in_else_block']}")
    
    # Overall assessment
    memory_timeout_ok = timeout_ok and target_ok
    single_model_ok = (route_analysis['has_unload_check'] and 
                      route_analysis['has_unload_call'] and 
                      not route_analysis['unload_in_else_block'])
    
    print("\n" + "="*60)
    print("STEP 1 RESULTS:")
    print("="*60)
    print(f"Memory Timeout (10s): {'✅ WORKING' if memory_timeout_ok else '❌ BROKEN'}")
    print(f"Single Model Enforcement: {'✅ WORKING' if single_model_ok else '❌ BROKEN'}")
    
    if route_analysis['unload_in_else_block']:
        print("\n🚨 CRITICAL ISSUE FOUND:")
        print("Model unloading only happens when memory pressure is LOW")
        print("When memory pressure is HIGH (>95%), models are NOT unloaded")
        print("This causes accumulation and routing failures")
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "step": 1,
        "unload_analysis": unload_analysis,
        "route_analysis": route_analysis,
        "memory_timeout_working": memory_timeout_ok,
        "single_model_enforcement_working": single_model_ok,
        "critical_issue": route_analysis['unload_in_else_block']
    }
    
    with open('validation_evidence/step1_timeout_verification.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved: validation_evidence/step1_timeout_verification.json")
    
    return memory_timeout_ok and single_model_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
