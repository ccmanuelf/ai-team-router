#!/usr/bin/env python3
"""Phase 4 Benchmarking Automation"""

import asyncio
import time
import json
import psutil
import aiohttp
from datetime import datetime
from typing import Dict, List, Any

class BenchmarkRunner:
    def __init__(self):
        self.results = []
        self.router_url = "http://localhost:11435"
        
    async def benchmark_model(self, prompt: str, expected_model: str = None) -> Dict:
        """Benchmark single request"""
        start_time = time.time()
        start_memory = psutil.virtual_memory().percent
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.router_url}/api/chat",
                    json={"prompt": prompt, "context": {}},
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        end_time = time.time()
                        end_memory = psutil.virtual_memory().percent
                        
                        return {
                            "prompt": prompt[:50] + "...",
                            "response_time": round(end_time - start_time, 2),
                            "model_used": data["metadata"]["model"],
                            "model_name": data["metadata"]["member"],
                            "expected_model": expected_model,
                            "routing_correct": expected_model in data["metadata"]["member"] if expected_model else None,
                            "response_length": len(data["response"]),
                            "memory_start": start_memory,
                            "memory_end": end_memory,
                            "success": True,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def run_benchmarks(self):
        """Execute benchmark suite"""
        test_cases = [
            # Simple tasks
            {
                "prompt": "Write a Python function to sort a list of dictionaries by a key",
                "category": "simple_coding",
                "expected": "mistral_versatile"
            },
            {
                "prompt": "Create a Vue 3 component with reactive data and computed properties", 
                "category": "vue_coding",
                "expected": "deepcoder_primary"
            },
            {
                "prompt": "Generate VBA code for Excel inventory reconciliation with 150,000 rows",
                "category": "excel_vba", 
                "expected": "qwen_analyst"
            },
            {
                "prompt": "Build a Laravel API endpoint with validation and authentication",
                "category": "laravel_php",
                "expected": "deepseek_legacy"
            },
            {
                "prompt": "Analyze this screenshot for UI elements and layout structure",
                "category": "vision",
                "expected": "granite_vision"
            },
            # Complex tasks
            {
                "prompt": "Design a complete e-commerce product catalog system with Vue 3, Pinia state management, TypeScript interfaces, and component composition API including search, filtering, pagination, and shopping cart functionality",
                "category": "complex_vue",
                "expected": "deepcoder_primary"
            },
            {
                "prompt": "Create a comprehensive Laravel application with user authentication, role-based permissions, API resources, database migrations, seeders, form requests, custom middleware, event listeners, and job queues for processing background tasks",
                "category": "complex_laravel", 
                "expected": "deepseek_legacy"
            }
        ]
        
        print("=== PHASE 4 BENCHMARKING START ===")
        print(f"Testing {len(test_cases)} scenarios...")
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] {test['category']}")
            result = await self.benchmark_model(test["prompt"], test.get("expected"))
            result.update({
                "test_id": i,
                "category": test["category"], 
                "expected_model": test.get("expected")
            })
            self.results.append(result)
            
            if result["success"]:
                routing = "✅" if result.get("routing_correct") else "⚠️"
                print(f"  {routing} {result['response_time']}s | {result['model_name']}")
            else:
                print(f"  ❌ Failed: {result['error']}")
            
            # Brief pause between tests
            await asyncio.sleep(2)
        
        return self.results
    
    def generate_report(self):
        """Generate benchmark report"""
        if not self.results:
            return "No results to report"
            
        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]
        
        report = f"""
# PHASE 4 BENCHMARK RESULTS

## Summary
- **Total Tests**: {len(self.results)}
- **Successful**: {len(successful)}
- **Failed**: {len(failed)}
- **Success Rate**: {len(successful)/len(self.results)*100:.1f}%

## Performance Metrics
"""
        
        if successful:
            times = [r["response_time"] for r in successful]
            report += f"""
- **Average Response Time**: {sum(times)/len(times):.1f}s
- **Fastest Response**: {min(times):.1f}s  
- **Slowest Response**: {max(times):.1f}s
"""
            
            # Routing accuracy
            routing_tests = [r for r in successful if r.get("routing_correct") is not None]
            if routing_tests:
                correct_routing = sum(1 for r in routing_tests if r["routing_correct"])
                report += f"- **Routing Accuracy**: {correct_routing}/{len(routing_tests)} ({correct_routing/len(routing_tests)*100:.1f}%)\n"
        
        report += "\n## Detailed Results\n"
        for result in self.results:
            if result["success"]:
                status = "✅" if result.get("routing_correct", True) else "⚠️"
                report += f"- {status} **{result['category']}**: {result['response_time']}s | {result['model_name']}\n"
            else:
                report += f"- ❌ **{result['category']}**: Failed - {result['error']}\n"
        
        return report

async def main():
    """Run benchmarking suite"""
    runner = BenchmarkRunner()
    results = await runner.run_benchmarks()
    report = runner.generate_report()
    
    # Save results
    with open('validation_evidence/phase4_benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    with open('validation_evidence/phase4_benchmark_report.md', 'w') as f:
        f.write(report)
    
    print("\n" + "="*50)
    print(report)
    print("\nResults saved to validation_evidence/")

if __name__ == "__main__":
    asyncio.run(main())
