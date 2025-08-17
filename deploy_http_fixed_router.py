#!/usr/bin/env python3
"""
Deploy HTTP-Fixed Router
========================

Quick deployment script for the router with HTTP connection fixes applied

Usage: python3 deploy_http_fixed_router.py
"""

import subprocess
import time
import requests
import os
import signal
import sys

def stop_existing_router():
    """Stop any existing router processes"""
    try:
        # Kill any existing router processes
        subprocess.run(["pkill", "-f", "ai_team_router"], capture_output=True)
        subprocess.run(["pkill", "-f", "uvicorn.*11435"], capture_output=True)
        time.sleep(2)
        print("✅ Stopped existing router processes")
    except Exception as e:
        print(f"⚠️ Could not stop existing processes: {e}")

def start_fixed_router():
    """Start the HTTP-fixed router"""
    
    print("🚀 Starting HTTP-fixed router...")
    
    # Use the complete router from http_connection_fixes.py
    # Since we couldn't complete the full file creation due to length limits,
    # we'll copy the existing router and patch it
    
    router_script = """
import sys
sys.path.append('.')
from http_connection_fixes import OptimizedHTTPClient

# Import and patch the existing router
import src.ai_team_router as original_router

# Replace the aiohttp client with our optimized requests client
original_router.AITeamRouter.__init__ = lambda self: self._init_with_http_fixes()

def _init_with_http_fixes(self):
    self.active_member = None
    self.team_members = self._initialize_team()
    self.request_history = []
    self.performance_metrics = {}
    self.emergency_mode = False
    self.min_system_memory_gb = 2.0
    
    # Use our optimized HTTP client instead of aiohttp
    self.ollama_client = OptimizedHTTPClient()
    
    if self.ollama_client.check_connection():
        print("✅ Ollama connection verified with HTTP fixes")
    else:
        print("❌ Ollama connection failed")

original_router.AITeamRouter._init_with_http_fixes = _init_with_http_fixes

# Run the patched router
if __name__ == "__main__":
    original_router.main()
"""
    
    # Write temporary patched router
    with open("router_http_patched.py", "w") as f:
        f.write(router_script)
    
    try:
        # Start the router
        process = subprocess.Popen([
            "python3", "router_http_patched.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Waiting for router to start...")
        time.sleep(10)
        
        # Test if router is responding
        try:
            response = requests.get("http://localhost:11435/health", timeout=5)
            if response.status_code == 200:
                print("✅ Router started successfully with HTTP fixes!")
                return process
            else:
                print(f"❌ Router health check failed: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Router not responding: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start router: {e}")
        return None

def test_fixed_router():
    """Test the fixed router with the same scenarios that failed"""
    
    test_cases = [
        {
            "name": "Vue.js Task",
            "prompt": "Create a Vue.js component with reactive data binding"
        },
        {
            "name": "Excel VBA Task", 
            "prompt": "Generate VBA code to process 150000 rows in Excel"
        },
        {
            "name": "Laravel Task",
            "prompt": "Create a Laravel API endpoint with validation"
        }
    ]
    
    print("\n🧪 Testing HTTP-fixed router...")
    
    results = []
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:11435/api/chat",
                json={
                    "prompt": test_case["prompt"],
                    "context": {}
                },
                timeout=360  # 6 minutes
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                model_used = result.get("metadata", {}).get("member", "unknown")
                print(f"✅ SUCCESS: {model_used} ({elapsed:.1f}s)")
                results.append({"success": True, "duration": elapsed})
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                results.append({"success": False, "error": f"HTTP {response.status_code}"})
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            print(f"⏰ TIMEOUT after {elapsed:.1f}s")
            results.append({"success": False, "error": "timeout"})
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({"success": False, "error": str(e)})
    
    # Results summary
    successful = len([r for r in results if r["success"]])
    total = len(results)
    
    print(f"\n📋 TEST RESULTS:")
    print(f"✅ Successful: {successful}/{total} ({(successful/total*100):.1f}%)")
    
    if successful == total:
        print("🎉 ALL TESTS PASSED - HTTP fixes working!")
        print("🏆 Ready for Phase 4A completion")
    elif successful > 0:
        print(f"⚠️ PARTIAL SUCCESS - {successful} tests passed")
        print("🔧 HTTP fixes helping but may need refinement")
    else:
        print("❌ ALL TESTS FAILED - HTTP fixes not working")
        print("🔧 Need alternative approach")
    
    return successful, total

def main():
    """Main deployment process"""
    
    print("🔧 DEPLOYING HTTP-FIXED AI TEAM ROUTER")
    print("=" * 50)
    print("Background: Phase 4A identified HTTP connection timeout issues")
    print("Solution: Replace aiohttp with optimized requests library")
    print("=" * 50)
    
    try:
        # Step 1: Stop existing router
        stop_existing_router()
        
        # Step 2: Start fixed router
        router_process = start_fixed_router()
        
        if not router_process:
            print("❌ Failed to start router - deployment aborted")
            return False
        
        # Step 3: Test the fixes
        successful, total = test_fixed_router()
        
        # Step 4: Decision
        if successful == total:
            print("\n🎯 DEPLOYMENT SUCCESSFUL!")
            print("Router is now running with HTTP fixes applied")
            print("Phase 4A should now achieve 70%+ routing accuracy")
            
            # Keep router running
            print("\n📝 Router is running on http://localhost:11435")
            print("Press Ctrl+C to stop...")
            
            try:
                router_process.wait()
            except KeyboardInterrupt:
                print("\n⏹️ Stopping router...")
                router_process.terminate()
                router_process.wait()
                
        else:
            print(f"\n⚠️ DEPLOYMENT PARTIAL SUCCESS ({successful}/{total})")
            print("Some tests still failing - investigate further")
            
            # Stop router
            router_process.terminate()
            router_process.wait()
        
        # Cleanup
        if os.path.exists("router_http_patched.py"):
            os.remove("router_http_patched.py")
            
        return successful == total
        
    except KeyboardInterrupt:
        print("\n⏹️ Deployment interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
