#!/usr/bin/env python3
"""
Phase 4A Quick Validation Test
"""
import subprocess
import json
import time
import os

def quick_phase4a_test():
    """Run Phase 4A with extended timeouts"""
    os.chdir('/Users/mcampos.cerda/Documents/Programming/ai-team-router')
    
    # Kill existing
    subprocess.run(['pkill', '-f', 'ai_team_router.py'], capture_output=True)
    time.sleep(2)
    
    # Start router  
    process = subprocess.Popen(['python3', 'src/ai_team_router.py'], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(8)
    
    # Quick tests with realistic prompts
    tests = [
        {"name": "Simple", "prompt": "Hello", "expect": "small"},
        {"name": "Vue", "prompt": "Create Vue component", "expect": "deepcoder"}
    ]
    
    results = []
    for test in tests:
        print(f"Testing {test['name']}...")
        try:
            result = subprocess.run([
                'curl', '-s', '-X', 'POST', '--max-time', '90',
                'http://localhost:11435/api/chat',
                '-H', 'Content-Type: application/json', 
                '-d', json.dumps({"prompt": test["prompt"]})
            ], capture_output=True, text=True, timeout=100)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if 'error' not in data.get('metadata', {}):
                    model = data.get('metadata', {}).get('member', 'unknown')
                    print(f"✅ {model}")
                    results.append({"test": test['name'], "success": True, "model": model})
                else:
                    print(f"❌ Error in response")
                    results.append({"test": test['name'], "success": False})
            else:
                print(f"❌ HTTP error")
                results.append({"test": test['name'], "success": False})
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({"test": test['name'], "success": False})
    
    success_rate = len([r for r in results if r.get('success')]) / len(results) * 100
    print(f"\nSuccess rate: {success_rate:.0f}%")
    
    # Cleanup
    subprocess.run(['pkill', '-f', 'ai_team_router.py'], capture_output=True)
    
    return success_rate >= 50

if __name__ == "__main__":
    success = quick_phase4a_test()
    exit(0 if success else 1)
