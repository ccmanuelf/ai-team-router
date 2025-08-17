#!/usr/bin/env python3
"""
Test Step 1 Fix: Memory Timeout Restored
"""

import subprocess
import json
import time
import os

def test_router_fix():
    """Test the memory threshold fix"""
    print("="*50)
    print("STEP 1 FIX TEST: Memory Timeout Restored")
    print("="*50)
    
    os.chdir('/Users/mcampos.cerda/Documents/Programming/ai-team-router')
    
    # Restart router with fix
    print("1. Restarting router with fix...")
    subprocess.run(['pkill', '-f', 'ai_team_router.py'], capture_output=True)
    time.sleep(2)
    
    # Start router
    process = subprocess.Popen(['python3', 'src/ai_team_router.py'], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
    time.sleep(5)
    
    # Test Vue.js request (should use DeepCoder now)
    print("2. Testing Vue.js routing...")
    result = subprocess.run([
        'curl', '-s', '-X', 'POST', 
        'http://localhost:11435/api/chat',
        '-H', 'Content-Type: application/json',
        '-d', '{"prompt": "Create a Vue.js component", "context": {}}'
    ], capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            metadata = data.get('metadata', {})
            model_used = metadata.get('member', 'unknown')
            model_id = metadata.get('model', 'unknown')
            
            print(f"Model used: {model_used}")
            print(f"Model ID: {model_id}")
            
            if 'deepcoder' in model_id.lower():
                print("✅ SUCCESS: Vue.js using DeepCoder (fixed!)")
                success = True
            elif 'gemma' in model_id.lower() and '1b' in model_id:
                print("❌ STILL BROKEN: Vue.js using tiny model")
                success = False
            else:
                print(f"⚠️ PARTIAL: Vue.js using {model_used} (not ideal)")
                success = True
        except:
            print("❌ Error parsing response")
            success = False
    else:
        print("❌ Request failed")
        success = False
    
    # Get memory status
    result = subprocess.run(['curl', '-s', 'http://localhost:11435/api/team/status'], 
                           capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            system = data.get('system', {})
            pressure = system.get('memory_pressure', 0)
            available = system.get('available_memory_gb', 0)
            print(f"Memory pressure: {pressure:.1f}%")
            print(f"Available memory: {available:.2f}GB")
        except:
            pass
    
    print("="*50)
    print(f"STEP 1 FIX: {'✅ SUCCESS' if success else '❌ FAILED'}")
    return success

if __name__ == "__main__":
    success = test_router_fix()
    exit(0 if success else 1)
