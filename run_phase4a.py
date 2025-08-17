#!/usr/bin/env python3
"""Phase 4A Benchmarking - Terminal Test Script"""

import asyncio
import aiohttp
import time
import json
import psutil
from datetime import datetime

async def benchmark_single(prompt, category, expected_model):
    """Run single benchmark test"""
    start = time.time()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:11435/api/chat',
                json={'prompt': prompt, 'context': {}},
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    elapsed = time.time() - start
                    
                    return {
                        'category': category,
                        'success': True,
                        'response_time': round(elapsed, 1),
                        'model_used': data['metadata']['member'],
                        'expected_model': expected_model,
                        'routing_correct': expected_model.lower() in data['metadata']['member'].lower(),
                        'response_length': len(data['response']),
                        'response_preview': data['response'][:100] + '...'
                    }
                else:
                    return {
                        'category': category,
                        'success': False,
                        'error': f'HTTP {response.status}'
                    }
    except Exception as e:
        return {
            'category': category,
            'success': False,
            'error': str(e)
        }

async def run_phase4a():
    """Execute Phase 4A benchmarking"""
    
    tests = [
        {
            'prompt': 'Write a Python function to sort a list of dictionaries by a key',
            'category': 'simple_coding',
            'expected': 'mistral'
        },
        {
            'prompt': 'Create a Vue 3 component with reactive data and computed properties',
            'category': 'vue_coding', 
            'expected': 'deepcoder'
        },
        {
            'prompt': 'Generate VBA code for Excel inventory reconciliation with 150,000 rows',
            'category': 'excel_vba',
            'expected': 'qwen'
        },
        {
            'prompt': 'Build a Laravel API endpoint with validation and authentication',
            'category': 'laravel_php',
            'expected': 'deepseek'
        },
        {
            'prompt': 'Analyze this screenshot for UI elements and layout structure',
            'category': 'vision',
            'expected': 'granite'
        }
    ]
    
    print("=== PHASE 4A BENCHMARKING START ===")
    print(f"Time: {datetime.now()}")
    
    # Check system status
    mem = psutil.virtual_memory()
    print(f"Memory: {mem.percent:.1f}% used, {mem.available/(1024**3):.1f}GB available")
    
    # Test router health
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:11435/health') as response:
                if response.status == 200:
                    print("✅ Router health check passed")
                else:
                    print(f"⚠️ Router health check failed: {response.status}")
    except Exception as e:
        print(f"❌ Router unreachable: {e}")
        return
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print(f"\n[{i}/{len(tests)}] Testing {test['category']}...")
        
        result = await benchmark_single(test['prompt'], test['category'], test['expected'])
        results.append(result)
        
        if result['success']:
            routing = "✅" if result['routing_correct'] else "⚠️"
            print(f"  {routing} {result['response_time']}s | {result['model_used']}")
            print(f"  Preview: {result['response_preview']}")
        else:
            print(f"  ❌ Failed: {result['error']}")
        
        # Pause between tests
        if i < len(tests):
            print("  Waiting 3s...")
            await asyncio.sleep(3)
    
    # Generate summary
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print("\n" + "="*60)
    print("PHASE 4A RESULTS SUMMARY")
    print("="*60)
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Success Rate: {len(successful)/len(results)*100:.1f}%")
    
    if successful:
        times = [r['response_time'] for r in successful]
        correct_routing = sum(1 for r in successful if r['routing_correct'])
        
        print(f"\nPerformance Metrics:")
        print(f"Average Response Time: {sum(times)/len(times):.1f}s")
        print(f"Fastest Response: {min(times):.1f}s")
        print(f"Slowest Response: {max(times):.1f}s")
        print(f"Routing Accuracy: {correct_routing}/{len(successful)} ({correct_routing/len(successful)*100:.1f}%)")
    
    print(f"\nDetailed Results:")
    for r in results:
        if r['success']:
            status = "✅" if r['routing_correct'] else "⚠️"
            print(f"{status} {r['category']}: {r['response_time']}s | {r['model_used']}")
        else:
            print(f"❌ {r['category']}: Failed - {r['error']}")
    
    # Save results
    with open('validation_evidence/phase4a_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Determine phase status
    if len(successful) == len(results):
        print(f"\n🎉 PHASE 4A PASSED - All tests successful")
        status = "PASSED"
    elif len(successful) > 0:
        print(f"\n⚠️ PHASE 4A PARTIAL - {len(successful)}/{len(results)} tests passed")
        status = "PARTIAL"
    else:
        print(f"\n❌ PHASE 4A FAILED - No tests passed")
        status = "FAILED"
    
    # Save summary report
    report = f"""# Phase 4A Benchmarking Results

## Status: {status}

### Summary
- **Total Tests**: {len(results)}
- **Successful**: {len(successful)}
- **Failed**: {len(failed)}
- **Success Rate**: {len(successful)/len(results)*100:.1f}%

### Performance Metrics
"""
    
    if successful:
        times = [r['response_time'] for r in successful]
        correct_routing = sum(1 for r in successful if r['routing_correct'])
        report += f"""- **Average Response Time**: {sum(times)/len(times):.1f}s
- **Fastest Response**: {min(times):.1f}s  
- **Slowest Response**: {max(times):.1f}s
- **Routing Accuracy**: {correct_routing}/{len(successful)} ({correct_routing/len(successful)*100:.1f}%)
"""
    
    report += f"\n### Detailed Results\n"
    for r in results:
        if r['success']:
            status_icon = "✅" if r['routing_correct'] else "⚠️"
            report += f"- {status_icon} **{r['category']}**: {r['response_time']}s | {r['model_used']}\n"
        else:
            report += f"- ❌ **{r['category']}**: Failed - {r['error']}\n"
    
    report += f"\n---\n*Phase 4A executed: {datetime.now()}*"
    
    with open('validation_evidence/phase4a_report.md', 'w') as f:
        f.write(report)
    
    print(f"\nResults saved:")
    print(f"- validation_evidence/phase4a_results.json")
    print(f"- validation_evidence/phase4a_report.md")
    
    return status == "PASSED"

if __name__ == "__main__":
    success = asyncio.run(run_phase4a())
    if success:
        print("\n✅ Phase 4A completed successfully - ready for Phase 4B")
    else:
        print("\n❌ Phase 4A failed - must fix issues before proceeding")
