#!/usr/bin/env python3
"""
Unload Timing Test - Measure actual model unload behavior
"""

import asyncio
import json
import logging
import time
import sys
import os

# Add src directory to path
src_path = '/Users/mcampos.cerda/Documents/Programming/ai-team-router/src'
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from ai_team_router import AITeamRouter
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    sys.exit(1)
import psutil

# Enhanced logging for testing
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - UNLOAD_TEST - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/Users/mcampos.cerda/Documents/Programming/ai-team-router/logs/unload_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def test_unload_timing():
    """Test actual unload behavior with different models"""
    
    print("🔬 UNLOAD TIMING TEST - Data-Driven Analysis")
    print("=" * 60)
    
    router = AITeamRouter()
    
    # Test models from smallest to largest
    test_models = [
        ("gemma_tiny", "gemma3:1b", 0.8),
        ("granite_vision", "granite3.2-vision:2b", 2.4),
        ("granite_moe", "granite3.1-moe:3b", 2.0),
        ("gemma_medium", "gemma3:4b", 3.3),
        ("mistral_versatile", "mistral:latest", 4.4),
        ("granite_enterprise", "granite3.3:8b", 4.9),
    ]
    
    results = []
    
    for member_id, model_id, expected_memory in test_models:
        print(f"\n🧪 Testing: {member_id} ({model_id}) - Expected: {expected_memory}GB")
        
        # Check initial memory
        initial_mem = psutil.virtual_memory()
        initial_available = initial_mem.available / (1024**3)
        
        print(f"   📊 Initial memory: {initial_available:.2f}GB available ({initial_mem.percent:.1f}% used)")
        
        # Skip if insufficient memory to load
        if initial_available < expected_memory + 0.5:
            print(f"   ⏭️  SKIP: Insufficient memory ({initial_available:.1f}GB < {expected_memory + 0.5:.1f}GB needed)")
            continue
        
        try:
            # Load the model by making a simple request
            print(f"   🔄 Loading {model_id}...")
            load_start = time.time()
            
            response = await router.route_request(
                prompt="Hello, respond with just 'OK'",
                context={"force_model": member_id}
            )
            
            load_time = time.time() - load_start
            
            # Check memory after loading
            loaded_mem = psutil.virtual_memory()
            loaded_available = loaded_mem.available / (1024**3)
            memory_used = initial_available - loaded_available
            
            print(f"   ✅ Loaded in {load_time:.1f}s, using {memory_used:.2f}GB")
            print(f"   📊 After load: {loaded_available:.2f}GB available ({loaded_mem.percent:.1f}% used)")
            
            # Now test unload with our new mechanism
            print(f"   🔄 Testing unload with new timing mechanism...")
            unload_start = time.time()
            
            unload_success = await router._unload_model(model_id)
            
            unload_time = time.time() - unload_start
            
            # Check final memory
            final_mem = psutil.virtual_memory()
            final_available = final_mem.available / (1024**3)
            memory_released = final_available - loaded_available
            
            result = {
                "model": member_id,
                "model_id": model_id,
                "expected_memory_gb": expected_memory,
                "load_time_s": load_time,
                "unload_time_s": unload_time,
                "memory_used_gb": memory_used,
                "memory_released_gb": memory_released,
                "unload_success": unload_success,
                "final_available_gb": final_available,
                "final_memory_percent": final_mem.percent
            }
            
            results.append(result)
            
            print(f"   🏁 Unload completed in {unload_time:.1f}s")
            print(f"   📊 Released {memory_released:.2f}GB (success: {unload_success})")
            print(f"   📊 Final: {final_available:.2f}GB available ({final_mem.percent:.1f}% used)")
            
            # Wait between tests
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            continue
    
    # Generate report
    print("\n" + "=" * 60)
    print("📊 UNLOAD TIMING ANALYSIS REPORT")
    print("=" * 60)
    
    if not results:
        print("❌ No successful tests - insufficient memory or system issues")
        return
    
    # Save detailed results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = f"/Users/mcampos.cerda/Documents/Programming/ai-team-router/validation_evidence/unload_timing_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "test_type": "unload_timing_analysis",
            "system_info": {
                "platform": "M3 Pro",
                "total_memory_gb": psutil.virtual_memory().total / (1024**3)
            },
            "results": results
        }, f, indent=2)
    
    # Analyze timing patterns
    successful_unloads = [r for r in results if r["unload_success"]]
    
    if successful_unloads:
        avg_unload_time = sum(r["unload_time_s"] for r in successful_unloads) / len(successful_unloads)
        max_unload_time = max(r["unload_time_s"] for r in successful_unloads)
        min_unload_time = min(r["unload_time_s"] for r in successful_unloads)
        
        print(f"✅ Successful unloads: {len(successful_unloads)}/{len(results)}")
        print(f"⏱️  Average unload time: {avg_unload_time:.1f}s")
        print(f"⏱️  Range: {min_unload_time:.1f}s - {max_unload_time:.1f}s")
        print(f"💡 RECOMMENDATION: Set unload timeout to {max_unload_time + 1:.1f}s")
        
        # Memory release analysis
        good_releases = [r for r in successful_unloads if r["memory_released_gb"] >= 0.5]
        print(f"💾 Good memory releases (≥0.5GB): {len(good_releases)}/{len(successful_unloads)}")
        
        if good_releases:
            avg_release = sum(r["memory_released_gb"] for r in good_releases) / len(good_releases)
            print(f"💾 Average release: {avg_release:.2f}GB")
    
    print(f"\n📁 Detailed results saved to: {report_file}")
    print(f"📁 Live logs in: /Users/mcampos.cerda/Documents/Programming/ai-team-router/logs/unload_test.log")

if __name__ == "__main__":
    print("🚀 Starting unload timing analysis...")
    asyncio.run(test_unload_timing())
