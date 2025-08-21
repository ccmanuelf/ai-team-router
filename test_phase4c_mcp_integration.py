#!/usr/bin/env python3
"""
Phase 4C Test 1: MCP Server Integration Validation
Tests MCP server functionality, tools, and Claude Desktop integration
"""

import asyncio
import json
import subprocess
import sys
import time
from datetime import datetime

async def test_mcp_server_import():
    """Test 1.1: MCP Server Import"""
    print("=== TEST 1.1: MCP Server Import ===")
    
    try:
        sys.path.insert(0, '/Users/mcampos.cerda/Documents/Programming/ai-team-router/src')
        from mcp_server import MCPServer
        
        server = MCPServer()
        team_count = len(server.router.team_members)
        
        print(f"✅ MCP Server imported successfully")
        print(f"✅ Router initialized with {team_count} team members")
        return True, {"team_members": team_count}
        
    except Exception as e:
        print(f"❌ MCP Server import failed: {e}")
        return False, {"error": str(e)}

async def test_mcp_tools_listing():
    """Test 1.2: MCP Tools Listing"""
    print("\n=== TEST 1.2: MCP Tools Listing ===")
    
    try:
        from mcp_server import MCPServer
        server = MCPServer()
        
        # Test list_tools method
        tools_response = await server.handle_list_tools()
        tools = tools_response.get("tools", [])
        
        print(f"✅ Tools listing successful: {len(tools)} tools found")
        
        # Verify expected tools
        tool_names = [tool["name"] for tool in tools]
        expected_tools = ["smart_route", "system_status", "optimize_memory"]
        
        for expected in expected_tools:
            if expected in tool_names:
                print(f"✅ {expected}: Found")
            else:
                print(f"❌ {expected}: Missing")
        
        # Count model-specific tools
        model_tools = [name for name in tool_names if name.startswith("ask_")]
        print(f"✅ Model-specific tools: {len(model_tools)}")
        
        return True, {
            "total_tools": len(tools),
            "expected_tools_found": all(tool in tool_names for tool in expected_tools),
            "model_tools": len(model_tools),
            "all_tools": tool_names
        }
        
    except Exception as e:
        print(f"❌ Tools listing failed: {e}")
        return False, {"error": str(e)}

async def test_mcp_smart_route():
    """Test 1.3: MCP Smart Route Tool"""
    print("\n=== TEST 1.3: MCP Smart Route Tool ===")
    
    try:
        from mcp_server import MCPServer
        server = MCPServer()
        
        # Test smart_route tool
        params = {
            "name": "smart_route",
            "arguments": {
                "prompt": "Quick test: What is 2+2?",
                "priority": "normal",
                "temperature": 0.3
            }
        }
        
        start_time = time.time()
        response = await server.handle_call_tool(params)
        elapsed = time.time() - start_time
        
        if "error" in response:
            print(f"❌ Smart route failed: {response['error']}")
            return False, {"error": response["error"]}
        
        content = response.get("content", [])
        metadata = response.get("metadata", {})
        
        if content and len(content) > 0:
            text_response = content[0].get("text", "")
            model_used = metadata.get("model_used", "unknown")
            member_name = metadata.get("member_name", "unknown")
            
            print(f"✅ Smart route successful")
            print(f"✅ Model used: {model_used} ({member_name})")
            print(f"✅ Response time: {elapsed:.2f}s")
            print(f"✅ Response preview: {text_response[:100]}...")
            
            return True, {
                "model_used": model_used,
                "member_name": member_name,
                "response_time": elapsed,
                "response_length": len(text_response),
                "has_response": len(text_response) > 0
            }
        else:
            print(f"❌ Empty response from smart route")
            return False, {"error": "Empty response"}
            
    except Exception as e:
        print(f"❌ Smart route test failed: {e}")
        return False, {"error": str(e)}

async def test_mcp_system_status():
    """Test 1.4: MCP System Status Tool"""
    print("\n=== TEST 1.4: MCP System Status Tool ===")
    
    try:
        from mcp_server import MCPServer
        server = MCPServer()
        
        params = {
            "name": "system_status",
            "arguments": {}
        }
        
        response = await server.handle_call_tool(params)
        
        if "error" in response:
            print(f"❌ System status failed: {response['error']}")
            return False, {"error": response["error"]}
        
        content = response.get("content", [])
        if content and len(content) > 0:
            status_text = content[0].get("text", "")
            status_data = json.loads(status_text)
            
            # Verify expected fields
            required_fields = ["active_member", "team_size", "system", "team_members"]
            missing_fields = [field for field in required_fields if field not in status_data]
            
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
                return False, {"error": f"Missing fields: {missing_fields}"}
            
            team_size = status_data.get("team_size", 0)
            memory_gb = status_data.get("system", {}).get("total_memory_gb", 0)
            available_gb = status_data.get("system", {}).get("available_memory_gb", 0)
            
            print(f"✅ System status successful")
            print(f"✅ Team size: {team_size}")
            print(f"✅ Total memory: {memory_gb:.1f}GB")
            print(f"✅ Available memory: {available_gb:.1f}GB")
            
            return True, {
                "team_size": team_size,
                "total_memory_gb": memory_gb,
                "available_memory_gb": available_gb,
                "has_all_fields": len(missing_fields) == 0
            }
        else:
            print(f"❌ Empty response from system status")
            return False, {"error": "Empty response"}
            
    except Exception as e:
        print(f"❌ System status test failed: {e}")
        return False, {"error": str(e)}

async def test_mcp_memory_optimization():
    """Test 1.5: MCP Memory Optimization Tool"""
    print("\n=== TEST 1.5: MCP Memory Optimization Tool ===")
    
    try:
        from mcp_server import MCPServer
        server = MCPServer()
        
        params = {
            "name": "optimize_memory",
            "arguments": {
                "force_unload": False
            }
        }
        
        response = await server.handle_call_tool(params)
        
        if "error" in response:
            print(f"❌ Memory optimization failed: {response['error']}")
            return False, {"error": response["error"]}
        
        content = response.get("content", [])
        if content and len(content) > 0:
            result_text = content[0].get("text", "")
            
            print(f"✅ Memory optimization successful")
            print(f"✅ Result: {result_text[:200]}...")
            
            return True, {
                "optimization_completed": True,
                "result_length": len(result_text)
            }
        else:
            print(f"❌ Empty response from memory optimization")
            return False, {"error": "Empty response"}
            
    except Exception as e:
        print(f"❌ Memory optimization test failed: {e}")
        return False, {"error": str(e)}

async def main():
    """Run MCP Server Integration Tests"""
    print("="*60)
    print("🧪 PHASE 4C - TEST 1: MCP SERVER INTEGRATION")
    print("="*60)
    print(f"Time: {datetime.now()}")
    print("")
    
    results = {}
    
    # Run tests
    test_results = [
        ("import", await test_mcp_server_import()),
        ("tools_listing", await test_mcp_tools_listing()),
        ("smart_route", await test_mcp_smart_route()),
        ("system_status", await test_mcp_system_status()),
        ("memory_optimization", await test_mcp_memory_optimization())
    ]
    
    # Collect results
    passed_tests = 0
    for test_name, (success, data) in test_results:
        results[test_name] = {"success": success, "data": data}
        if success:
            passed_tests += 1
    
    # Summary
    total_tests = len(test_results)
    print(f"\n{'='*60}")
    print("MCP SERVER INTEGRATION TEST SUMMARY")
    print("="*60)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    for test_name, (success, data) in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    overall_success = passed_tests == total_tests
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    # Save results
    test_evidence = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "mcp_server_integration",
        "phase": "4C",
        "test_number": 1,
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "success_rate": (passed_tests/total_tests)*100,
        "overall_success": overall_success,
        "detailed_results": results
    }
    
    filename = f"validation_evidence/phase4c_test1_mcp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(test_evidence, f, indent=2)
    
    print(f"\n📊 Results saved: {filename}")
    print("="*60)
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
