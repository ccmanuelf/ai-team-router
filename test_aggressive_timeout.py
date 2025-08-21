#!/usr/bin/env python3
"""
Aggressive Timeout Test - Force timeout scenarios
Tests extremely complex tasks to trigger timeout conditions
"""

import requests
import time
import json
from datetime import datetime

def test_timeout_scenarios():
    """Test scenarios designed to trigger timeouts"""
    print("="*60)
    print("🧪 AGGRESSIVE TIMEOUT TEST - FORCE TIMEOUT SCENARIOS")
    print("="*60)
    
    # Extremely complex tasks designed to exceed limits
    timeout_test_cases = [
        {
            "name": "Massive Code Generation",
            "prompt": """Write a complete Python web application with the following requirements:
1. Django backend with 15 models (User, Product, Order, Category, Review, etc.)
2. Full CRUD operations for each model
3. REST API with Django REST Framework
4. Authentication and authorization system
5. Complete frontend with HTML/CSS/JavaScript
6. Database migrations and seed data
7. Unit tests for all models and views
8. Deployment configuration (Docker, nginx)
9. Documentation with API examples
10. Error handling and logging
11. Email system integration
12. Payment processing integration
13. Search functionality with Elasticsearch
14. Caching with Redis
15. Background tasks with Celery
Include ALL code files with complete implementations, no placeholders.""",
            "expected": "Should timeout or take >300s"
        },
        {
            "name": "Complex Algorithm Implementation",
            "prompt": """Implement the following algorithms from scratch in Python with complete code:
1. Advanced sorting algorithms: QuickSort, MergeSort, HeapSort, RadixSort
2. Graph algorithms: Dijkstra, A*, Floyd-Warshall, Kruskal's MST
3. Dynamic programming: Longest Common Subsequence, Knapsack, Edit Distance
4. Machine learning: Linear Regression, K-Means, Decision Tree from scratch
5. Data structures: Red-Black Tree, B-Tree, Trie, Segment Tree
6. String algorithms: KMP, Rabin-Karp, Suffix Array
7. Numerical algorithms: FFT, Matrix multiplication, Prime factorization
8. Complete test suite for each algorithm
9. Performance benchmarking code
10. Visualization code for each algorithm
Include complete implementations with detailed comments and examples.""",
            "expected": "Should timeout or take >300s"
        },
        {
            "name": "Comprehensive Data Analysis",
            "prompt": """Perform complete data analysis on a hypothetical dataset with 1 million rows:
1. Data cleaning and preprocessing (handle missing values, outliers, duplicates)
2. Exploratory data analysis with 50+ statistical measures
3. Feature engineering (create 30+ new features)
4. Multiple machine learning models (10+ algorithms)
5. Cross-validation and hyperparameter tuning
6. Model comparison and selection
7. Feature importance analysis
8. Prediction intervals and uncertainty quantification
9. Interactive visualizations (20+ plots)
10. Complete report with interpretation
11. Production deployment code
12. Monitoring and alerting setup
13. A/B testing framework
14. Real-time prediction API
15. Database optimization strategies
Write complete Python code for each step with full implementation.""",
            "expected": "Should timeout or take >300s"
        }
    ]
    
    results = []
    
    for test_case in timeout_test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        
        # Test with 300s timeout (original problematic timeout)
        result_300s = test_with_timeout(test_case, 300)
        
        # Test with 600s timeout (if 300s succeeds)
        result_600s = None
        if result_300s.get("success"):
            print("  🤔 300s succeeded, testing 600s...")
            result_600s = test_with_timeout(test_case, 600)
        
        results.append({
            "test": test_case["name"],
            "result_300s": result_300s,
            "result_600s": result_600s
        })
    
    analyze_timeout_results(results)
    return results

def test_with_timeout(test_case, timeout_seconds):
    """Test with specific timeout"""
    print(f"  ⏱️ Testing with {timeout_seconds}s timeout...")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepcoder:latest",
                "prompt": test_case["prompt"],
                "stream": False
            },
            timeout=timeout_seconds
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")
            
            print(f"    ✅ Completed in {elapsed:.1f}s")
            print(f"    📊 Response: {len(response_text)} chars")
            
            return {
                "success": True,
                "time": elapsed,
                "response_length": len(response_text),
                "timeout": False,
                "timeout_limit": timeout_seconds
            }
        else:
            print(f"    ❌ HTTP {response.status_code}")
            return {
                "success": False, 
                "error": f"HTTP {response.status_code}",
                "timeout_limit": timeout_seconds
            }
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"    ⏰ TIMEOUT after {elapsed:.1f}s")
        return {
            "success": False,
            "timeout": True,
            "time": elapsed,
            "timeout_limit": timeout_seconds
        }
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"    ❌ Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "time": elapsed,
            "timeout_limit": timeout_seconds
        }

def analyze_timeout_results(results):
    """Analyze timeout test results"""
    print(f"\n{'='*60}")
    print("AGGRESSIVE TIMEOUT TEST RESULTS")
    print("="*60)
    
    timeouts_300s = sum(1 for r in results if r["result_300s"].get("timeout", False))
    timeouts_600s = sum(1 for r in results if r.get("result_600s") and r["result_600s"].get("timeout", False))
    
    print(f"Tests that timed out at 300s: {timeouts_300s}/{len(results)}")
    print(f"Tests that timed out at 600s: {timeouts_600s}/{len([r for r in results if r.get('result_600s')])}")
    
    # Detailed analysis
    for result in results:
        test_name = result["test"]
        result_300 = result["result_300s"]
        result_600 = result.get("result_600s")
        
        print(f"\n📋 {test_name}:")
        
        if result_300.get("timeout"):
            print(f"  ⏰ 300s: TIMEOUT")
        elif result_300.get("success"):
            print(f"  ✅ 300s: {result_300['time']:.1f}s ({result_300['response_length']} chars)")
        else:
            print(f"  ❌ 300s: {result_300.get('error', 'Failed')}")
        
        if result_600:
            if result_600.get("timeout"):
                print(f"  ⏰ 600s: TIMEOUT")
            elif result_600.get("success"):
                print(f"  ✅ 600s: {result_600['time']:.1f}s ({result_600['response_length']} chars)")
            else:
                print(f"  ❌ 600s: {result_600.get('error', 'Failed')}")
    
    # Recommendations
    if timeouts_300s > 0:
        print(f"\n🎯 FINDING: Successfully triggered timeouts at 300s")
        print(f"📈 RECOMMENDATION: Original timeout issue reproduced")
        if timeouts_600s == 0:
            print(f"✅ SOLUTION: 600s timeout resolves the issue")
        else:
            print(f"⚠️ COMPLEX: Some tasks need >600s - streaming might help")
    else:
        print(f"\n🤔 FINDING: No timeouts triggered even with complex tasks")
        print(f"📋 POSSIBLE CAUSES:")
        print(f"   - Model optimization since original tests")
        print(f"   - Different model context/state")
        print(f"   - Hardware performance variations")
        print(f"   - Task complexity still insufficient")

def main():
    """Run aggressive timeout tests"""
    print(f"Starting aggressive timeout test at {datetime.now()}")
    
    # Verify Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama not responding")
            return False
    except:
        print("❌ Ollama not running")
        return False
    
    # Run tests
    results = test_timeout_scenarios()
    
    # Save results
    filename = f"aggressive_timeout_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved: {filename}")
    return True

if __name__ == "__main__":
    main()
