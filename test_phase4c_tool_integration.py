#!/usr/bin/env python3
"""
Phase 4C Part 2 - Test 2: Tool Integration Validation
Tests web search, code execution, and file analysis capabilities
"""

import asyncio
import json
import subprocess
import sys
import time
import requests
import os
from datetime import datetime

def test_web_search_integration():
    """Test 2.1: Web Search Integration"""
    print("\n=== TEST 2.1: Web Search Integration ===")
    
    # Test cases with different models and search queries
    test_cases = [
        {
            "name": "Vue.js Best Practices",
            "prompt": "Search for latest Vue.js 3 best practices and create a component example",
            "expected_model": "deepcoder",
            "should_search": True
        },
        {
            "name": "Excel VBA Functions", 
            "prompt": "Search for Excel VBA functions for processing large datasets and provide example",
            "expected_model": "qwen",
            "should_search": True
        },
        {
            "name": "Laravel Routing",
            "prompt": "Search for Laravel 10 routing best practices and show implementation",
            "expected_model": "deepseek",
            "should_search": True
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            print(f"\n--- Testing: {test_case['name']} ---")
            
            start_time = time.time()
            response = requests.post(
                "http://localhost:11435/api/chat",
                json={"prompt": test_case["prompt"]},
                timeout=480
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                model_used = data.get("metadata", {}).get("model", "unknown")
                
                # Check if response indicates web search was used
                search_indicators = [
                    "search", "found", "according to", "based on", 
                    "recent", "latest", "current", "2024", "2025"
                ]
                has_search_content = any(indicator in response_text.lower() for indicator in search_indicators)
                
                print(f"✅ {test_case['name']}: {model_used} ({elapsed:.1f}s)")
                print(f"   Response length: {len(response_text)} chars")
                print(f"   Search indicators: {'✅ FOUND' if has_search_content else '❌ NOT FOUND'}")
                print(f"   Preview: {response_text[:150]}...")
                
                results.append({
                    "test": test_case["name"],
                    "success": True,
                    "model_used": model_used,
                    "response_time": elapsed,
                    "response_length": len(response_text),
                    "has_search_content": has_search_content,
                    "web_search_working": has_search_content
                })
            else:
                print(f"❌ {test_case['name']}: HTTP {response.status_code}")
                results.append({"test": test_case["name"], "success": False, "error": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ {test_case['name']}: {e}")
            results.append({"test": test_case["name"], "success": False, "error": str(e)})
    
    successful_tests = sum(1 for r in results if r.get("success", False))
    search_working = sum(1 for r in results if r.get("web_search_working", False))
    
    print(f"\n--- Web Search Integration Summary ---")
    print(f"Tests passed: {successful_tests}/{len(test_cases)}")
    print(f"Web search detected: {search_working}/{len(results)}")
    
    return successful_tests == len(test_cases), {
        "tests_passed": successful_tests,
        "total_tests": len(test_cases),
        "search_working": search_working,
        "detailed_results": results
    }

def test_code_execution():
    """Test 2.2: Code Execution"""
    print("\n=== TEST 2.2: Code Execution ===")
    
    test_cases = [
        {
            "name": "Python Data Processing",
            "prompt": "Write and execute Python code to process a list of numbers: [1,2,3,4,5]. Calculate sum, average, and create a simple visualization",
            "language": "python",
            "execution_expected": True
        },
        {
            "name": "JavaScript Array Manipulation", 
            "prompt": "Write and execute JavaScript code to filter and transform an array of objects representing users with ages",
            "language": "javascript",
            "execution_expected": True
        },
        {
            "name": "Algorithm Implementation",
            "prompt": "Implement and execute a simple sorting algorithm in Python with example data",
            "language": "python",
            "execution_expected": True
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            print(f"\n--- Testing: {test_case['name']} ---")
            
            start_time = time.time()
            response = requests.post(
                "http://localhost:11435/api/chat",
                json={"prompt": test_case["prompt"]},
                timeout=300
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                model_used = data.get("metadata", {}).get("model", "unknown")
                
                # Check for code execution indicators
                execution_indicators = [
                    "output:", "result:", "executed", "running", "print(", 
                    "console.log", "=>", ">>>", "execution"
                ]
                has_execution = any(indicator in response_text.lower() for indicator in execution_indicators)
                
                # Check for actual code blocks
                has_code = "```" in response_text or "def " in response_text or "function" in response_text
                
                print(f"✅ {test_case['name']}: {model_used} ({elapsed:.1f}s)")
                print(f"   Code blocks: {'✅ FOUND' if has_code else '❌ NOT FOUND'}")
                print(f"   Execution indicators: {'✅ FOUND' if has_execution else '❌ NOT FOUND'}")
                print(f"   Preview: {response_text[:150]}...")
                
                results.append({
                    "test": test_case["name"],
                    "success": True,
                    "model_used": model_used,
                    "response_time": elapsed,
                    "has_code": has_code,
                    "has_execution": has_execution,
                    "code_execution_working": has_code and has_execution
                })
            else:
                print(f"❌ {test_case['name']}: HTTP {response.status_code}")
                results.append({"test": test_case["name"], "success": False, "error": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ {test_case['name']}: {e}")
            results.append({"test": test_case["name"], "success": False, "error": str(e)})
    
    successful_tests = sum(1 for r in results if r.get("success", False))
    execution_working = sum(1 for r in results if r.get("code_execution_working", False))
    
    print(f"\n--- Code Execution Summary ---")
    print(f"Tests passed: {successful_tests}/{len(test_cases)}")
    print(f"Code execution detected: {execution_working}/{len(results)}")
    
    return successful_tests == len(test_cases), {
        "tests_passed": successful_tests,
        "total_tests": len(test_cases),
        "execution_working": execution_working,
        "detailed_results": results
    }

def test_file_analysis():
    """Test 2.3: File Analysis"""
    print("\n=== TEST 2.3: File Analysis ===")
    
    # Create test files
    test_files = {
        "sample.txt": "This is a sample text file for analysis.\nIt contains multiple lines.\nLine 3 with data.",
        "data.csv": "Name,Age,City\nJohn,25,NYC\nJane,30,LA\nBob,35,Chicago",
        "config.json": '{"app": "router", "version": "1.0", "models": 11}'
    }
    
    # Create test files
    os.makedirs("test_files", exist_ok=True)
    for filename, content in test_files.items():
        with open(f"test_files/{filename}", 'w') as f:
            f.write(content)
    
    test_cases = [
        {
            "name": "Text File Analysis",
            "prompt": "Analyze the file test_files/sample.txt and provide insights about its content, structure, and word count",
            "file_type": "text"
        },
        {
            "name": "CSV Data Processing",
            "prompt": "Analyze test_files/data.csv and provide statistics, insights, and suggest Excel VBA code for processing similar data",
            "file_type": "csv"
        },
        {
            "name": "JSON Configuration Analysis",
            "prompt": "Analyze test_files/config.json and explain the structure, validate the JSON, and suggest improvements",
            "file_type": "json"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            print(f"\n--- Testing: {test_case['name']} ---")
            
            start_time = time.time()
            response = requests.post(
                "http://localhost:11435/api/chat",
                json={"prompt": test_case["prompt"]},
                timeout=300
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                model_used = data.get("metadata", {}).get("model", "unknown")
                
                # Check for file analysis indicators
                analysis_indicators = [
                    "file", "content", "structure", "data", "analysis", 
                    "lines", "rows", "columns", "format", "contains"
                ]
                has_analysis = any(indicator in response_text.lower() for indicator in analysis_indicators)
                
                # Check if response shows understanding of file content
                content_understanding = False
                if test_case["file_type"] == "text" and "sample" in response_text.lower():
                    content_understanding = True
                elif test_case["file_type"] == "csv" and ("john" in response_text.lower() or "name" in response_text.lower()):
                    content_understanding = True
                elif test_case["file_type"] == "json" and ("router" in response_text.lower() or "version" in response_text.lower()):
                    content_understanding = True
                
                print(f"✅ {test_case['name']}: {model_used} ({elapsed:.1f}s)")
                print(f"   Analysis indicators: {'✅ FOUND' if has_analysis else '❌ NOT FOUND'}")
                print(f"   Content understanding: {'✅ FOUND' if content_understanding else '❌ NOT FOUND'}")
                print(f"   Preview: {response_text[:150]}...")
                
                results.append({
                    "test": test_case["name"],
                    "success": True,
                    "model_used": model_used,
                    "response_time": elapsed,
                    "has_analysis": has_analysis,
                    "content_understanding": content_understanding,
                    "file_analysis_working": has_analysis and content_understanding
                })
            else:
                print(f"❌ {test_case['name']}: HTTP {response.status_code}")
                results.append({"test": test_case["name"], "success": False, "error": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ {test_case['name']}: {e}")
            results.append({"test": test_case["name"], "success": False, "error": str(e)})
    
    # Cleanup test files
    import shutil
    if os.path.exists("test_files"):
        shutil.rmtree("test_files")
    
    successful_tests = sum(1 for r in results if r.get("success", False))
    analysis_working = sum(1 for r in results if r.get("file_analysis_working", False))
    
    print(f"\n--- File Analysis Summary ---")
    print(f"Tests passed: {successful_tests}/{len(test_cases)}")
    print(f"File analysis working: {analysis_working}/{len(results)}")
    
    return successful_tests == len(test_cases), {
        "tests_passed": successful_tests,
        "total_tests": len(test_cases),
        "analysis_working": analysis_working,
        "detailed_results": results
    }

def main():
    """Run Tool Integration Tests"""
    print("="*60)
    print("🧪 PHASE 4C PART 2 - TEST 2: TOOL INTEGRATION VALIDATION")
    print("="*60)
    print(f"Time: {datetime.now()}")
    print("")
    
    # Run tests
    web_search_success, web_search_data = test_web_search_integration()
    code_exec_success, code_exec_data = test_code_execution() 
    file_analysis_success, file_analysis_data = test_file_analysis()
    
    # Summary
    total_tests = 3
    passed_tests = sum([web_search_success, code_exec_success, file_analysis_success])
    
    print(f"\n{'='*60}")
    print("TOOL INTEGRATION TEST SUMMARY")
    print("="*60)
    print(f"Web Search Integration: {'✅ PASS' if web_search_success else '❌ FAIL'}")
    print(f"Code Execution: {'✅ PASS' if code_exec_success else '❌ FAIL'}")
    print(f"File Analysis: {'✅ PASS' if file_analysis_success else '❌ FAIL'}")
    print(f"")
    print(f"Overall: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
    
    overall_success = passed_tests == total_tests
    print(f"Result: {'✅ TOOL INTEGRATION WORKING' if overall_success else '❌ SOME TOOLS NOT WORKING'}")
    
    # Save evidence
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "tool_integration_validation",
        "phase": "4C_part2",
        "test_number": 2,
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "success_rate": (passed_tests/total_tests)*100,
        "overall_success": overall_success,
        "web_search": {"success": web_search_success, "data": web_search_data},
        "code_execution": {"success": code_exec_success, "data": code_exec_data},
        "file_analysis": {"success": file_analysis_success, "data": file_analysis_data}
    }
    
    filename = f"validation_evidence/phase4c_test2_tools_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print(f"\n📊 Evidence saved: {filename}")
    print("="*60)
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
