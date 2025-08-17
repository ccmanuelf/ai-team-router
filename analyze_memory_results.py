#!/usr/bin/env python3
"""
Memory Analysis Utility
=======================

Analyze results from collaborative validation tests
Parse JSON results and generate readable reports

Usage: python3 analyze_memory_results.py [results_file.json]
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def analyze_memory_unload_results(results):
    """Analyze memory unload investigation results"""
    
    print("🔍 MEMORY UNLOAD ANALYSIS")
    print("=" * 50)
    
    # Basic info
    test_model = results.get("test_model", "unknown")
    load_duration = results.get("load_duration_seconds", 0)
    unload_duration = results.get("unload_duration_seconds", 0)
    unload_effective = results.get("unload_effective", False)
    
    print(f"🎯 Model tested: {test_model}")
    print(f"⏱️ Load time: {load_duration:.1f}s")
    print(f"⏱️ Unload time: {unload_duration:.1f}s")
    print(f"✅ Unload effective: {'YES' if unload_effective else 'NO'}")
    
    # Memory analysis
    memory_analysis = results.get("memory_analysis", {})
    peak_release = memory_analysis.get("peak_release", 0)
    final_release = memory_analysis.get("final_release", 0)
    
    print(f"📊 Peak memory release: {peak_release:.2f}GB")
    print(f"🏁 Final memory release: {final_release:.2f}GB")
    
    # Timeline analysis
    release_timeline = memory_analysis.get("release_timeline", [])
    if release_timeline:
        print(f"\n📈 Memory Release Timeline:")
        for event in release_timeline:
            time_s = event.get("time_seconds", 0)
            change_gb = event.get("memory_change_gb", 0)
            available_gb = event.get("available_gb", 0)
            print(f"  t={time_s:2d}s: {change_gb:+.2f}GB (available: {available_gb:.2f}GB)")
    
    # Determine timing issues
    estimated_model_memory = results.get("estimated_model_memory_gb", 0)
    if estimated_model_memory > 0:
        release_percentage = (final_release / estimated_model_memory) * 100
        print(f"\n🎯 Memory Release Efficiency: {release_percentage:.1f}%")
        
        if release_percentage >= 90:
            print("✅ EXCELLENT: Memory fully released")
        elif release_percentage >= 70:
            print("⚠️ GOOD: Most memory released")
        elif release_percentage >= 50:
            print("🔶 PARTIAL: Some memory released")
        else:
            print("❌ FAILED: Minimal memory released")
    
    # Timing analysis
    if unload_duration > 60:
        print(f"\n⏰ TIMING ISSUE: Unload took {unload_duration:.1f}s (>60s)")
        print("   Recommendation: Increase router timeout to 90s+")
    elif unload_duration > 30:
        print(f"\n⚠️ SLOW UNLOAD: {unload_duration:.1f}s (>30s)")
        print("   Recommendation: Increase router timeout to 60s")
    else:
        print(f"\n✅ ACCEPTABLE TIMING: {unload_duration:.1f}s")

def analyze_router_switching_results(results):
    """Analyze router model switching results"""
    
    print("\n🔀 ROUTER SWITCHING ANALYSIS")
    print("=" * 50)
    
    summary = results.get("summary", {})
    total_tests = summary.get("total_tests", 0)
    successful_tests = summary.get("successful_tests", 0)
    success_rate = summary.get("success_rate", 0) * 100
    routing_accuracy = summary.get("routing_accuracy", 0) * 100
    
    print(f"🔢 Total tests: {total_tests}")
    print(f"✅ Successful: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    print(f"🎯 Routing accuracy: {routing_accuracy:.1f}%")
    print(f"📈 Target: 70%")
    
    if routing_accuracy >= 70:
        print("🏆 PHASE 4A: PASSED")
    else:
        print("❌ PHASE 4A: FAILED")
    
    # Individual test analysis
    test_results = results.get("results", [])
    if test_results:
        print(f"\n📝 Individual Test Results:")
        for i, test in enumerate(test_results, 1):
            name = test.get("test_case", f"Test {i}")
            success = test.get("success", False)
            routing_correct = test.get("routing_correct", False)
            model_used = test.get("model_used", "unknown")
            memory_change = test.get("memory_change_gb", 0)
            
            status = "✅" if success else "❌"
            routing_status = "🎯" if routing_correct else "❌"
            
            print(f"  {i}. {name}: {status} {routing_status} {model_used} ({memory_change:+.2f}GB)")
            
            if not success:
                error = test.get("error", "Unknown error")
                print(f"     Error: {error}")
    
    # Memory pattern analysis
    memory_changes = [test.get("memory_change_gb", 0) for test in test_results]
    if memory_changes:
        total_memory_change = sum(memory_changes)
        print(f"\n📊 Memory Pattern Analysis:")
        print(f"   Total memory change: {total_memory_change:+.2f}GB")
        
        if total_memory_change < -2.0:
            print("   ⚠️ WARNING: Significant memory accumulation detected")
            print("   🔧 Action: Investigate model unloading mechanism")
        elif total_memory_change > 2.0:
            print("   ✅ GOOD: Memory appears to be releasing properly")
        else:
            print("   ➖ NEUTRAL: Minimal net memory change")

def generate_actionable_recommendations(unload_results, router_results):
    """Generate specific recommendations based on test results"""
    
    print("\n🎯 ACTIONABLE RECOMMENDATIONS")
    print("=" * 50)
    
    unload_effective = unload_results.get("unload_effective", False)
    routing_accuracy = router_results.get("summary", {}).get("routing_accuracy", 0) * 100
    unload_duration = unload_results.get("unload_duration_seconds", 0)
    
    recommendations = []
    
    # Memory unload recommendations
    if not unload_effective:
        recommendations.append({
            "priority": "HIGH",
            "area": "Memory Management",
            "issue": "Model unloading not releasing memory effectively",
            "action": "Investigate Ollama unload mechanism - may need different approach",
            "code_change": "Consider using 'ollama stop' command or process termination"
        })
    
    if unload_duration > 30:
        recommendations.append({
            "priority": "HIGH",
            "area": "Timeout Configuration",
            "issue": f"Unload takes {unload_duration:.1f}s but router timeout is 10s",
            "action": "Increase router unload timeout",
            "code_change": f"Change max_wait_time from 10.0 to {max(60, int(unload_duration + 10))}.0 seconds"
        })
    
    # Routing accuracy recommendations
    if routing_accuracy < 70:
        if unload_effective:
            recommendations.append({
                "priority": "MEDIUM",
                "area": "Routing Logic",
                "issue": "Memory unload working but routing accuracy still low",
                "action": "Investigate model selection logic and memory calculations",
                "code_change": "Review _get_available_memory_gb() calculation accuracy"
            })
        else:
            recommendations.append({
                "priority": "HIGH",
                "area": "Root Cause",
                "issue": "Low routing accuracy due to memory management failure",
                "action": "Fix memory unload mechanism first, then re-test routing",
                "code_change": "Focus on unload_model() function improvements"
            })
    
    # System-level recommendations
    recommendations.append({
        "priority": "LOW",
        "area": "Monitoring",
        "issue": "Need better visibility into memory management",
        "action": "Add enhanced logging to memory management functions",
        "code_change": "Add memory snapshots before/after each operation"
    })
    
    # Print recommendations
    for i, rec in enumerate(recommendations, 1):
        priority_color = {
            "HIGH": "🔴",
            "MEDIUM": "🟡", 
            "LOW": "🟢"
        }
        
        print(f"\n{i}. {priority_color[rec['priority']]} {rec['priority']} PRIORITY - {rec['area']}")
        print(f"   Issue: {rec['issue']}")
        print(f"   Action: {rec['action']}")
        print(f"   Code: {rec['code_change']}")
    
    return recommendations

def main():
    """Main analysis function"""
    
    # Determine which file to analyze
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    else:
        # Look for latest results file
        evidence_dir = Path("validation_evidence")
        if evidence_dir.exists():
            json_files = list(evidence_dir.glob("*collaborative_validation.json"))
            if json_files:
                results_file = max(json_files, key=lambda f: f.stat().st_mtime)
            else:
                print("❌ No collaborative validation results found")
                print("Usage: python3 analyze_memory_results.py [results_file.json]")
                return
        else:
            print("❌ validation_evidence directory not found")
            return
    
    print(f"📊 ANALYZING: {results_file}")
    print("=" * 80)
    
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Extract investigation results
        investigations = results.get("investigations", {})
        unload_results = investigations.get("memory_unload_timing", {})
        router_results = investigations.get("router_model_switching", {})
        
        # Run analyses
        if unload_results:
            analyze_memory_unload_results(unload_results)
        
        if router_results:
            analyze_router_switching_results(router_results)
        
        # Generate recommendations
        if unload_results and router_results:
            recommendations = generate_actionable_recommendations(unload_results, router_results)
        
        # Overall conclusion
        print("\n" + "=" * 80)
        print("🏁 OVERALL CONCLUSION")
        print("=" * 80)
        
        unload_working = unload_results.get("unload_effective", False)
        routing_accuracy = router_results.get("summary", {}).get("routing_accuracy", 0) * 100
        
        if unload_working and routing_accuracy >= 70:
            print("🎉 SUCCESS: Memory management and routing both working correctly")
            print("✅ Ready to proceed to Phase 4B")
        elif unload_working:
            print("⚠️ PARTIAL: Memory unload working but routing accuracy needs improvement")
            print("🔧 Focus: Investigate routing logic and memory calculations")
        else:
            print("❌ FAILURE: Memory unload mechanism not working effectively")
            print("🔧 Focus: Fix memory management before addressing routing")
        
        print(f"\n📈 Phase 4A Status: {'PASS' if routing_accuracy >= 70 else 'FAIL'} ({routing_accuracy:.1f}% routing accuracy)")
        
    except FileNotFoundError:
        print(f"❌ File not found: {results_file}")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in: {results_file}")
    except Exception as e:
        print(f"❌ Analysis error: {e}")

if __name__ == "__main__":
    main()
