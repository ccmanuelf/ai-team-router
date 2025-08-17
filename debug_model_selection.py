#!/usr/bin/env python3
"""
Debug Model Selection - Check why router defaults to Mistral
"""

import asyncio
import aiohttp
import json

async def debug_model_selection():
    """Debug why model selection always chooses Mistral"""
    
    test_prompts = [
        {
            'prompt': 'Create a Vue 3 component with TypeScript',
            'expected_domain': 'coding',
            'expected_model': 'deepcoder_primary'
        },
        {
            'prompt': 'Generate VBA macro for Excel with 150k rows',
            'expected_domain': 'enterprise', 
            'expected_model': 'qwen_analyst'
        },
        {
            'prompt': 'Build Laravel API with Eloquent ORM',
            'expected_domain': 'coding',
            'expected_model': 'deepseek_legacy'
        },
        {
            'prompt': 'Analyze this UI screenshot',
            'expected_domain': 'visual',
            'expected_model': 'granite_vision'
        }
    ]
    
    print("=== MODEL SELECTION DEBUG ===")
    
    # Check current system status
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:11435/api/team/status") as response:
            status = await response.json()
            print(f"Available Memory: {status['system']['available_memory_gb']:.2f}GB")
            print(f"Memory Pressure: {status['system']['memory_pressure']:.1f}%")
            print(f"Active Member: {status.get('active_member', 'None')}")
    
    # Check team members and their memory requirements
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:11435/api/team/members") as response:
            members = await response.json()
            
    print(f"\nTeam Members Memory Requirements:")
    memory_overhead = 0.5  # M3 Pro overhead
    for member_id, member in members.items():
        required = member['memory_gb'] + memory_overhead
        print(f"  {member_id}: {member['memory_gb']}GB + {memory_overhead}GB = {required:.1f}GB required")
    
    print(f"\nTesting model selection for different prompts:")
    
    for i, test in enumerate(test_prompts, 1):
        print(f"\n[{i}] Testing: {test['prompt'][:50]}...")
        print(f"    Expected Domain: {test['expected_domain']}")
        print(f"    Expected Model: {test['expected_model']}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'http://localhost:11435/api/chat',
                    json={
                        'prompt': test['prompt'],
                        'context': {'priority': 'normal'}
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        metadata = data.get('metadata', {})
                        requirements = metadata.get('requirements', {})
                        
                        print(f"    Actual Domain: {requirements.get('domain', 'unknown')}")
                        print(f"    Actual Model: {metadata.get('member', 'unknown')}")
                        print(f"    Model ID: {metadata.get('model', 'unknown')}")
                        print(f"    Complexity: {requirements.get('complexity', 'unknown')}")
                        
                        # Check if domain detection is working
                        domain_correct = requirements.get('domain') == test['expected_domain']
                        model_correct = test['expected_model'].lower() in metadata.get('member', '').lower()
                        
                        print(f"    Domain Detection: {'✅' if domain_correct else '❌'}")
                        print(f"    Model Selection: {'✅' if model_correct else '❌'}")
                        
                    else:
                        print(f"    ❌ Failed: HTTP {response.status}")
                        
        except Exception as e:
            print(f"    ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_model_selection())
