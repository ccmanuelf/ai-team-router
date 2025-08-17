#!/usr/bin/env python3
"""
Quick Memory Test - Single Model Load/Unload Cycle
==================================================

Simplified test to quickly verify memory unload behavior
Focus: Single DeepCoder model load → unload → memory monitoring

Usage: python3 quick_memory_test.py
"""

import requests
import time
import psutil
from datetime import datetime

def get_memory_gb():
    """Get available memory in GB"""
    return psutil.virtual_memory().available / (1024**3)

def test_single_model_unload():
    """Test single model unload with timing"""
    
    print("🎯 QUICK MEMORY TEST - DeepCoder Unload Timing")
    print("=" * 60)
    
    # Check Ollama service
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama service not available")
            return
        print("✅ Ollama service running")
    except:
        print("❌ Cannot connect to Ollama")
        return
    
    # Baseline memory
    baseline_memory = get_memory_gb()
    print(f"📊 Baseline memory: {baseline_memory:.2f}GB available")
    
    # Load DeepCoder
    print("\n🚀 Loading DeepCoder...")
    load_start = time.time()
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepcoder:latest",
                "prompt": "Hello",
                "stream": False,
                "options": {"num_ctx": 512}
            },
            timeout=180
        )
        
        load_time = time.time() - load_start
        
        if response.status_code == 200:
            print(f"✅ DeepCoder loaded in {load_time:.1f}s")
        else:
            print(f"❌ Load failed: HTTP {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Load error: {e}")
        return
    
    # Memory after load
    after_load_memory = get_memory_gb()
    model_memory_usage = baseline_memory - after_load_memory
    print(f"📊 After load: {after_load_memory:.2f}GB available")
    print(f"💾 Model using: {model_memory_usage:.2f}GB")
    
    # Wait for stabilization
    time.sleep(5)
    
    # Unload with monitoring
    print(f"\n📤 Unloading DeepCoder with 60s monitoring...")
    unload_start = time.time()
    
    # Send unload command
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepcoder:latest",
                "keep_alive": 0,
                "prompt": ""
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Unload command sent")
        else:
            print(f"⚠️ Unload command issue: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Unload command error: {e}")
    
    # Monitor memory for 60 seconds
    print("⏱️ Monitoring memory release...")
    peak_release = 0
    final_release = 0
    
    for i in range(30):  # 60 seconds, check every 2s
        time.sleep(2)
        current_memory = get_memory_gb()
        release = current_memory - after_load_memory
        
        if release > peak_release:
            peak_release = release
        
        if i % 5 == 0:  # Print every 10 seconds
            elapsed = i * 2
            print(f"  t={elapsed:2d}s: {current_memory:.2f}GB (+{release:.2f}GB released)")
    
    # Final measurements
    final_memory = get_memory_gb()
    final_release = final_memory - after_load_memory
    total_time = time.time() - unload_start
    
    print(f"\n📋 RESULTS ({total_time:.1f}s total)")
    print("=" * 40)
    print(f"💾 Model memory usage: {model_memory_usage:.2f}GB")
    print(f"🔺 Peak memory release: {peak_release:.2f}GB")
    print(f"🏁 Final memory release: {final_release:.2f}GB")
    
    # Analysis
    release_percentage = (final_release / model_memory_usage * 100) if model_memory_usage > 0 else 0
    
    if release_percentage >= 80:
        print(f"✅ UNLOAD SUCCESSFUL: {release_percentage:.1f}% of memory released")
    elif release_percentage >= 50:
        print(f"⚠️ PARTIAL UNLOAD: {release_percentage:.1f}% of memory released")
    else:
        print(f"❌ UNLOAD FAILED: {release_percentage:.1f}% of memory released")
    
    # Conclusion
    print(f"\n🎯 CONCLUSION:")
    if release_percentage >= 80:
        print("Memory unload mechanism appears to be working correctly")
    else:
        print("Memory unload mechanism may be failing - investigate further")
    
    return {
        "model_memory_usage": model_memory_usage,
        "peak_release": peak_release,
        "final_release": final_release,
        "release_percentage": release_percentage,
        "total_time": total_time
    }

if __name__ == "__main__":
    test_single_model_unload()
