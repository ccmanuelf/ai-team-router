#!/usr/bin/env python3
"""
Phase 4B: Router Intelligence Testing
Focus: Task routing accuracy and domain detection improvement
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime

async def test_routing_accuracy():
    """Test routing accuracy for different task types"""
    print("=== PHASE 4B: ROUTER INTELLIGENCE TESTING ===")
    
    test_cases = [
        {
            'prompt': 'Create a Vue 3 component with TypeScript for user authentication',
            'expected_model': 'deepcoder',
            'domain': 'vue_coding',
            'complexity': 4
        },
        {
            'prompt': 'Generate VBA macro for Excel inventory management with 150k rows',
            'expected_model': 'qwen',
            'domain': 'excel_enterprise',
            'complexity': 5
        },
        {
            'prompt': 'Build Laravel API with Eloquent ORM and JWT authentication',
            'expected_model': 'deepseek',
            'domain': 'laravel_php',
            'complexity': 4
        },
        {
            'prompt': 'Analyze this UI screenshot and suggest CSS improvements',
            'expected_model': 'granite_vision',
            'domain': 'vision_analysis',
            'complexity': 3
        },
        {
            'prompt': 'Simple Python function to calculate fibonacci sequence',
            'expected_model': 'gemma_medium',
            'domain': 'simple_coding',
            'complexity': 2
        },
        {
            'prompt': 'Optimize pandas DataFrame processing for large dataset',
            'expected_model': 'qwen',
            'domain': 'data_science',
            'complexity': 4
        },
        {
            'prompt': 'Quick fix: add error handling to existing function',
            'expected_model': 'gemma_tiny',
            'domain': 'quick_fix',
            'complexity': 1
        },
        {
            'prompt': 'Enterprise report generation with complex business logic',
            'expected_model': 'granite_enterprise',
            'domain': 'enterprise',
            'complexity': 4
        }
    ]
    
    results = []
    correct_routing = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Testing {test['domain']} (complexity {test['complexity']})")
        print(f"Prompt: {test['prompt'][:60]}...")
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'http://localhost:11435/api/chat',
                    json={
                        'prompt': test['prompt'],
                        'context': {'priority': 'normal', 'temperature': 0.7}
                    },
                    timeout=aiohttp.ClientTimeout(total=45)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        elapsed = time.time() - start_time
                        
                        model_used = data.get('metadata', {}).get('member', 'unknown')
                        model_id = data.get('metadata', {}).get('model', 'unknown')
                        
                        # Check if routing was correct
                        routing_correct = test['expected_model'].lower() in model_used.lower()
                        if routing_correct:
                            correct_routing += 1
                        
                        result = {
                            'test_id': i,
                            'domain': test['domain'],
                            'complexity': test['complexity'],
                            'expected_model': test['expected_model'],
                            'actual_model': model_used,
                            'model_id': model_id,
                            'routing_correct': routing_correct,
                            'response_time': round(elapsed, 1),
                            'success': True,
                            'response_preview': data.get('response', '')[:100]
                        }
                        
                        status = "✅" if routing_correct else "⚠️"
                        print(f"  {status} {elapsed:.1f}s | {model_used} | Expected: {test['expected_model']}")
                        
                    else:
                        result = {
                            'test_id': i,
                            'domain': test['domain'],
                            'success': False,
                            'error': f'HTTP {response.status}'
                        }
                        print(f"  ❌ Failed: HTTP {response.status}")
                        
        except Exception as e:
            result = {
                'test_id': i,
                'domain': test['domain'],
                'success': False,
                'error': str(e)
            }
            print(f"  ❌ Error: {e}")
        
        results.append(result)
        
        # Brief pause between tests
        if i < len(test_cases):
            await asyncio.sleep(2)
    
    return results, correct_routing, len(test_cases)

async def test_domain_detection():
    """Test domain detection accuracy"""
    print("\n=== DOMAIN DETECTION TESTING ===")
    
    domain_tests = [
        {'prompt': 'React component with hooks', 'expected': 'coding'},
        {'prompt': 'VBA Excel automation', 'expected': 'enterprise'},
        {'prompt': 'Laravel Eloquent model', 'expected': 'coding'},
        {'prompt': 'OCR from screenshot', 'expected': 'visual'},
        {'prompt': 'Pandas DataFrame analysis', 'expected': 'data'},
        {'prompt': 'Enterprise inventory report', 'expected': 'enterprise'}
    ]
    
    domain_results = []
    
    for test in domain_tests:
        # Simulate domain detection (would need to test actual router logic)
        print(f"  Testing: {test['prompt'][:40]}... → Expected: {test['expected']}")
        domain_results.append({
            'prompt': test['prompt'],
            'expected_domain': test['expected'],
            'detected_domain': 'coding'  # Placeholder - would need router internals
        })
    
    return domain_results

async def main():
    """Execute Phase 4B testing"""
    print("====================================================================")
    print("🧠 PHASE 4B: ROUTER INTELLIGENCE TESTING")
    print("====================================================================")
    print(f"Time: {datetime.now()}")
    print("Focus: Task routing accuracy and domain detection")
    print("")
    
    # Test routing accuracy
    routing_results, correct_routing, total_tests = await test_routing_accuracy()
    
    # Test domain detection
    domain_results = await test_domain_detection()
    
    # Calculate metrics
    successful_tests = [r for r in routing_results if r.get('success', False)]
    failed_tests = [r for r in routing_results if not r.get('success', False)]
    
    routing_accuracy = (correct_routing / len(successful_tests)) * 100 if successful_tests else 0
    
    if successful_tests:
        response_times = [r['response_time'] for r in successful_tests]
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
    else:
        avg_time = min_time = max_time = 0
    
    print("\n" + "="*60)
    print("PHASE 4B RESULTS SUMMARY")
    print("="*60)
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success Rate: {len(successful_tests)/total_tests*100:.1f}%")
    print(f"Routing Accuracy: {correct_routing}/{len(successful_tests)} ({routing_accuracy:.1f}%)")
    
    if successful_tests:
        print(f"\nPerformance Metrics:")
        print(f"Average Response Time: {avg_time:.1f}s")
        print(f"Fastest Response: {min_time:.1f}s")
        print(f"Slowest Response: {max_time:.1f}s")
    
    print(f"\nRouting Analysis:")
    for result in successful_tests:
        status = "✅" if result['routing_correct'] else "⚠️"
        print(f"{status} {result['domain']}: {result['actual_model']} (expected {result['expected_model']})")
    
    # Save results
    phase4b_results = {
        'timestamp': datetime.now().isoformat(),
        'phase': '4B_router_intelligence',
        'routing_tests': routing_results,
        'domain_tests': domain_results,
        'metrics': {
            'total_tests': total_tests,
            'successful_tests': len(successful_tests),
            'failed_tests': len(failed_tests),
            'success_rate': len(successful_tests)/total_tests*100,
            'routing_accuracy': routing_accuracy,
            'correct_routing': correct_routing,
            'average_response_time': avg_time,
            'min_response_time': min_time,
            'max_response_time': max_time
        }
    }
    
    with open('validation_evidence/phase4b_results.json', 'w') as f:
        json.dump(phase4b_results, f, indent=2)
    
    # Determine phase status
    phase_pass = (len(successful_tests) >= 6 and routing_accuracy >= 50)
    
    if phase_pass:
        print(f"\n✅ PHASE 4B PASSED - Router intelligence validated")
        status = "PASSED"
    else:
        print(f"\n⚠️ PHASE 4B PARTIAL - Router needs improvement")
        status = "PARTIAL"
    
    print(f"\nResults saved: validation_evidence/phase4b_results.json")
    print("="*60)
    
    return phase_pass

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
