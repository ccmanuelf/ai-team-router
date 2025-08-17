#!/usr/bin/env python3
"""
Phase 4A Collaborative Validation Script
=========================================

Focus: Memory management system investigation with detailed monitoring
Goal: Identify actual unload timing issues and memory accumulation patterns

Critical Investigation Areas:
1. Model unload timing (expected: 10s, suspected: 30-60s+)
2. Memory accumulation patterns
3. Ollama API response validation
4. Memory monitoring accuracy

Usage: python3 phase4a_collaborative_validation.py
"""

import subprocess
import json
import time
import os
import psutil
import requests
from datetime import datetime
from pathlib import Path

class MemoryMonitor:
    """Enhanced memory monitoring with timing analysis"""
    
    def __init__(self):
        self.baseline_memory = None
        self.monitoring_data = []
        
    def get_memory_snapshot(self):
        """Get detailed memory snapshot"""
        mem = psutil.virtual_memory()
        return {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "total_gb": mem.total / (1024**3),
            "available_gb": mem.available / (1024**3),
            "used_gb": mem.used / (1024**3),
            "percent_used": mem.percent,
            "free_gb": mem.free / (1024**3),
            "cached_gb": getattr(mem, 'cached', 0) / (1024**3),
            "buffers_gb": getattr(mem, 'buffers', 0) / (1024**3)
        }
    
    def set_baseline(self):
        """Set baseline memory state"""
        self.baseline_memory = self.get_memory_snapshot()
        print(f"🎯 Baseline Memory: {self.baseline_memory['available_gb']:.2f}GB available")
        return self.baseline_memory
    
    def monitor_memory_change(self, duration_seconds=60, interval_seconds=2):
        """Monitor memory changes over time"""
        start_time = time.time()
        self.monitoring_data = []
        
        print(f"📊 Starting memory monitoring for {duration_seconds}s (interval: {interval_seconds}s)")
        
        while (time.time() - start_time) < duration_seconds:
            snapshot = self.get_memory_snapshot()
            
            if self.baseline_memory:
                snapshot["change_from_baseline_gb"] = (
                    snapshot["available_gb"] - self.baseline_memory["available_gb"]
                )
            
            self.monitoring_data.append(snapshot)
            
            # Print progress
            elapsed = time.time() - start_time
            if len(self.monitoring_data) % 5 == 0:  # Every 10 seconds
                change = snapshot.get("change_from_baseline_gb", 0)
                print(f"  t={elapsed:.1f}s: {snapshot['available_gb']:.2f}GB available "
                      f"({change:+.2f}GB from baseline)")
            
            time.sleep(interval_seconds)
        
        return self.monitoring_data
    
    def analyze_memory_pattern(self):
        """Analyze memory release patterns"""
        if not self.monitoring_data:
            return None
        
        analysis = {
            "total_duration": len(self.monitoring_data) * 2,  # 2s intervals
            "memory_snapshots": len(self.monitoring_data),
            "peak_release": 0,
            "final_release": 0,
            "release_timeline": []
        }
        
        if self.baseline_memory:
            releases = [
                snap.get("change_from_baseline_gb", 0) 
                for snap in self.monitoring_data
            ]
            
            analysis["peak_release"] = max(releases) if releases else 0
            analysis["final_release"] = releases[-1] if releases else 0
            
            # Timeline of significant changes (>0.5GB)
            for i, snap in enumerate(self.monitoring_data):
                change = snap.get("change_from_baseline_gb", 0)
                if abs(change) > 0.5:
                    analysis["release_timeline"].append({
                        "time_seconds": i * 2,
                        "memory_change_gb": change,
                        "available_gb": snap["available_gb"]
                    })
        
        return analysis

class OllamaController:
    """Direct Ollama API control for testing"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        
    def check_service(self):
        """Verify Ollama service is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama service is running")
                return True
            else:
                print(f"❌ Ollama service error: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ollama service connection failed: {e}")
            return False
    
    def list_loaded_models(self):
        """Get currently loaded models in Ollama"""
        try:
            # Try to get process info (this is a workaround since Ollama doesn't expose loaded models directly)
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"📋 Available models: {len(models)}")
                return [model["name"] for model in models]
            return []
        except Exception as e:
            print(f"⚠️ Could not list models: {e}")
            return []
    
    def unload_model(self, model_name, timeout=120):
        """Send unload command to specific model"""
        try:
            print(f"🔄 Sending unload command for {model_name}")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_name,
                    "keep_alive": 0,
                    "prompt": ""
                },
                timeout=timeout
            )
            
            if response.status_code == 200:
                print(f"✅ Unload command sent successfully for {model_name}")
                return True
            else:
                print(f"❌ Unload command failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Unload command error: {e}")
            return False
    
    def load_model_test(self, model_name, timeout=180):
        """Test load a model with simple prompt"""
        try:
            print(f"🚀 Testing model load: {model_name}")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": "Hello",
                    "stream": False,
                    "options": {"num_ctx": 512}  # Minimal context
                },
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Model {model_name} loaded and responded")
                return True
            else:
                print(f"❌ Model load failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Model load error: {e}")
            return False

def run_memory_unload_investigation():
    """Core investigation: memory unload timing analysis"""
    
    print("="*80)
    print("🔍 MEMORY UNLOAD INVESTIGATION")
    print("="*80)
    print("Goal: Determine actual unload timing for large models")
    print("Expected: 10s timeout may be insufficient for 9GB models")
    print("="*80)
    
    monitor = MemoryMonitor()
    ollama = OllamaController()
    
    # Step 1: Verify Ollama service
    if not ollama.check_service():
        print("❌ Cannot proceed without Ollama service")
        return False
    
    # Step 2: Check available models
    available_models = ollama.list_loaded_models()
    
    # Step 3: Set memory baseline
    baseline = monitor.set_baseline()
    
    # Step 4: Test with DeepCoder (9GB model)
    test_model = "deepcoder:latest"
    print(f"\n🧪 TESTING LARGE MODEL: {test_model}")
    print("This will test the complete load → unload → memory release cycle")
    
    # Load model
    print(f"\n📥 Step 1: Loading {test_model}")
    load_start = time.time()
    load_success = ollama.load_model_test(test_model, timeout=300)  # 5 min timeout
    load_duration = time.time() - load_start
    
    if not load_success:
        print(f"❌ Could not load {test_model} for testing")
        return False
    
    print(f"⏱️ Model loaded in {load_duration:.1f}s")
    
    # Memory snapshot after load
    after_load = monitor.get_memory_snapshot()
    memory_used_by_model = baseline["available_gb"] - after_load["available_gb"]
    print(f"📊 Model appears to use {memory_used_by_model:.2f}GB")
    
    # Wait a moment for stabilization
    time.sleep(5)
    
    # Unload model with memory monitoring
    print(f"\n📤 Step 2: Unloading {test_model} with memory monitoring")
    unload_start = time.time()
    
    # Send unload command
    unload_success = ollama.unload_model(test_model, timeout=10)
    if not unload_success:
        print("⚠️ Unload command failed, but continuing memory monitoring")
    
    # Monitor memory for 90 seconds to see actual release pattern
    print("📊 Monitoring memory release for 90 seconds...")
    memory_data = monitor.monitor_memory_change(duration_seconds=90, interval_seconds=2)
    
    unload_total_duration = time.time() - unload_start
    
    # Analyze results
    analysis = monitor.analyze_memory_pattern()
    
    print(f"\n" + "="*60)
    print("📋 MEMORY UNLOAD ANALYSIS RESULTS")
    print("="*60)
    
    print(f"🕐 Total unload duration: {unload_total_duration:.1f}s")
    print(f"📊 Memory monitoring: {len(memory_data)} snapshots over {analysis['total_duration']}s")
    print(f"🔺 Peak memory release: {analysis['peak_release']:.2f}GB")
    print(f"🏁 Final memory release: {analysis['final_release']:.2f}GB")
    
    # Determine if unload was successful
    if analysis['final_release'] >= (memory_used_by_model * 0.8):  # 80% of used memory released
        print("✅ UNLOAD SUCCESSFUL: Model memory appears to be released")
        unload_effective = True
    else:
        print("❌ UNLOAD FAILED: Model memory not fully released")
        unload_effective = False
    
    # Timeline analysis
    if analysis['release_timeline']:
        print(f"\n📈 Memory Release Timeline:")
        for event in analysis['release_timeline']:
            print(f"  t={event['time_seconds']}s: {event['memory_change_gb']:+.2f}GB "
                  f"(available: {event['available_gb']:.2f}GB)")
    else:
        print("⚠️ No significant memory changes detected during monitoring period")
    
    # Generate detailed report
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "test_model": test_model,
        "load_duration_seconds": load_duration,
        "load_success": load_success,
        "unload_duration_seconds": unload_total_duration,
        "unload_command_success": unload_success,
        "unload_effective": unload_effective,
        "baseline_memory": baseline,
        "after_load_memory": after_load,
        "estimated_model_memory_gb": memory_used_by_model,
        "memory_analysis": analysis,
        "memory_monitoring_data": memory_data
    }
    
    # Save results
    results_file = "validation_evidence/memory_unload_investigation.json"
    os.makedirs("validation_evidence", exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return test_results

def run_router_model_switching_test():
    """Test router model switching with memory monitoring"""
    
    print("\n" + "="*80)
    print("🔀 ROUTER MODEL SWITCHING TEST")
    print("="*80)
    print("Goal: Test actual router behavior with memory monitoring")
    print("Expected: Identify where model switching fails")
    print("="*80)
    
    monitor = MemoryMonitor()
    
    # Start router in background
    print("🚀 Starting router...")
    router_process = subprocess.Popen(
        ['python3', 'src/ai_team_router.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for router to start
    time.sleep(10)
    
    # Set baseline
    baseline = monitor.set_baseline()
    
    # Test cases designed to trigger model switching
    test_cases = [
        {
            "name": "Vue.js Task",
            "prompt": "Create a Vue.js component with reactive data binding",
            "expected_model": "DeepCoder",
            "expected_size_gb": 9.0
        },
        {
            "name": "Excel VBA Task", 
            "prompt": "Generate VBA code to process 150000 rows in Excel",
            "expected_model": "Qwen",
            "expected_size_gb": 9.0
        },
        {
            "name": "Laravel Task",
            "prompt": "Create a Laravel API endpoint with validation",
            "expected_model": "DeepSeek", 
            "expected_size_gb": 8.9
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Prompt: {test_case['prompt']}")
        print(f"Expected: {test_case['expected_model']} ({test_case['expected_size_gb']}GB)")
        
        # Memory before request
        before_request = monitor.get_memory_snapshot()
        
        try:
            # Make request to router
            response = requests.post(
                "http://localhost:11435/api/chat",
                json={
                    "prompt": test_case["prompt"],
                    "context": {}
                },
                timeout=300  # 5 minute timeout
            )
            
            # Memory after request
            after_request = monitor.get_memory_snapshot()
            memory_change = after_request["available_gb"] - before_request["available_gb"]
            
            if response.status_code == 200:
                result_data = response.json()
                metadata = result_data.get("metadata", {})
                
                test_result = {
                    "test_case": test_case["name"],
                    "success": True,
                    "model_used": metadata.get("member", "unknown"),
                    "model_id": metadata.get("model", "unknown"),
                    "response_time": metadata.get("elapsed_time", 0),
                    "memory_before_gb": before_request["available_gb"],
                    "memory_after_gb": after_request["available_gb"],
                    "memory_change_gb": memory_change,
                    "routing_correct": test_case["expected_model"] in metadata.get("member", "")
                }
                
                print(f"✅ Success: {metadata.get('member', 'unknown')} "
                      f"({metadata.get('elapsed_time', 0):.1f}s)")
                print(f"📊 Memory: {memory_change:+.2f}GB change")
                print(f"🎯 Routing: {'✅ CORRECT' if test_result['routing_correct'] else '❌ WRONG'}")
                
            else:
                test_result = {
                    "test_case": test_case["name"],
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "memory_before_gb": before_request["available_gb"],
                    "memory_after_gb": after_request["available_gb"],
                    "memory_change_gb": memory_change,
                    "routing_correct": False
                }
                
                print(f"❌ Failed: HTTP {response.status_code}")
                print(f"📊 Memory: {memory_change:+.2f}GB change")
        
        except Exception as e:
            after_request = monitor.get_memory_snapshot()
            memory_change = after_request["available_gb"] - before_request["available_gb"]
            
            test_result = {
                "test_case": test_case["name"],
                "success": False,
                "error": str(e),
                "memory_before_gb": before_request["available_gb"],
                "memory_after_gb": after_request["available_gb"],
                "memory_change_gb": memory_change,
                "routing_correct": False
            }
            
            print(f"❌ Exception: {e}")
            print(f"📊 Memory: {memory_change:+.2f}GB change")
        
        results.append(test_result)
        
        # Wait between tests to allow any memory settling
        if i < len(test_cases):
            print("⏳ Waiting 30s before next test...")
            time.sleep(30)
    
    # Stop router
    router_process.terminate()
    router_process.wait()
    
    # Calculate overall results
    successful_tests = len([r for r in results if r["success"]])
    correct_routing = len([r for r in results if r.get("routing_correct", False)])
    
    print(f"\n" + "="*60)
    print("📋 ROUTER SWITCHING TEST RESULTS")
    print("="*60)
    print(f"🔢 Total tests: {len(test_cases)}")
    print(f"✅ Successful: {successful_tests}/{len(test_cases)} ({(successful_tests/len(test_cases)*100):.1f}%)")
    print(f"🎯 Correct routing: {correct_routing}/{len(test_cases)} ({(correct_routing/len(test_cases)*100):.1f}%)")
    
    # Save results
    router_results = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "router_model_switching",
        "baseline_memory": baseline,
        "test_cases": test_cases,
        "results": results,
        "summary": {
            "total_tests": len(test_cases),
            "successful_tests": successful_tests,
            "success_rate": successful_tests / len(test_cases),
            "correct_routing": correct_routing,
            "routing_accuracy": correct_routing / len(test_cases)
        }
    }
    
    results_file = "validation_evidence/router_switching_investigation.json"
    with open(results_file, 'w') as f:
        json.dump(router_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return router_results

def main():
    """Main collaborative validation execution"""
    
    print("🎯 PHASE 4A COLLABORATIVE VALIDATION")
    print("=" * 80)
    print("Focus: Memory management system investigation")
    print("Computer restart: ✅ Completed")
    print("Ready for detailed memory behavior analysis")
    print("=" * 80)
    
    # Ensure validation evidence directory exists
    os.makedirs("validation_evidence", exist_ok=True)
    
    try:
        # Investigation 1: Direct memory unload timing
        print("\n🔬 INVESTIGATION 1: Memory Unload Timing Analysis")
        unload_results = run_memory_unload_investigation()
        
        if not unload_results:
            print("❌ Investigation 1 failed - cannot proceed to router testing")
            return
        
        # Investigation 2: Router model switching behavior
        print("\n🔬 INVESTIGATION 2: Router Model Switching Analysis")
        router_results = run_router_model_switching_test()
        
        # Generate comprehensive report
        comprehensive_results = {
            "validation_timestamp": datetime.now().isoformat(),
            "validation_type": "phase4a_collaborative_memory_investigation",
            "computer_restart_completed": True,
            "investigations": {
                "memory_unload_timing": unload_results,
                "router_model_switching": router_results
            },
            "key_findings": {
                "unload_effective": unload_results.get("unload_effective", False),
                "routing_accuracy": router_results["summary"]["routing_accuracy"],
                "memory_management_working": unload_results.get("unload_effective", False)
            }
        }
        
        # Save comprehensive report
        final_report = "validation_evidence/phase4a_collaborative_validation.json"
        with open(final_report, 'w') as f:
            json.dump(comprehensive_results, f, indent=2)
        
        print(f"\n" + "="*80)
        print("📋 PHASE 4A COLLABORATIVE VALIDATION COMPLETE")
        print("="*80)
        
        # Summary
        unload_working = unload_results.get("unload_effective", False)
        routing_accuracy = router_results["summary"]["routing_accuracy"] * 100
        
        print(f"🔧 Memory unload working: {'✅ YES' if unload_working else '❌ NO'}")
        print(f"🎯 Routing accuracy: {routing_accuracy:.1f}%")
        print(f"📊 Target accuracy: 70%")
        print(f"🏆 Phase 4A status: {'✅ PASS' if routing_accuracy >= 70 else '❌ FAIL'}")
        
        print(f"\n💾 Comprehensive report: {final_report}")
        print("\n🤝 Ready for collaborative analysis of results")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Validation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
