#!/usr/bin/env python3
"""
MCP Server for AI Team Router - Enhanced Version
Implements Model Context Protocol for integration with Claude Desktop and Zed
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, List, Optional
import logging

# Add router to path
sys.path.insert(0, '/Users/mcampos.cerda/Documents/Programming/ai-team-router/src')

from ai_team_router import AITeamRouter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server implementation for Enhanced AI Team Router"""
    
    def __init__(self):
        self.router = AITeamRouter()
        logger.info(f"Enhanced MCP Server initialized with {len(self.router.team_members)} models")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests"""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "initialize":
            return await self.handle_initialize(params)
        elif method == "list_tools":
            return await self.handle_list_tools()
        elif method == "call_tool":
            return await self.handle_call_tool(params)
        elif method == "chat":
            return await self.handle_chat(params)
        else:
            return {"error": f"Unknown method: {method}"}
    
    async def handle_initialize(self, params: Dict) -> Dict:
        """Initialize MCP connection"""
        return {
            "protocolVersion": "2024.11.05",
            "serverInfo": {
                "name": "ai-team-router-enhanced",
                "version": "2.0.0"
            },
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": True
            }
        }
    
    async def handle_list_tools(self) -> Dict:
        """List available tools with enhanced capabilities"""
        tools = []
        
        # Add each model as a tool
        for member_id, member in self.router.team_members.items():
            tools.append({
                "name": f"ask_{member_id}",
                "description": f"Ask {member.name} ({member.model_id}) - Expert in: {', '.join(member.expertise[:3])} | Memory: {member.memory_gb}GB",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The question or task"
                        },
                        "context": {
                            "type": "object",
                            "description": "Optional context with temperature, priority"
                        }
                    },
                    "required": ["prompt"]
                }
            })
        
        # Enhanced routing tool
        tools.append({
            "name": "smart_route",
            "description": "Automatically route to optimal model with enhanced memory management and 10s timeout",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The question or task"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "normal", "high"],
                        "description": "Task priority for model selection"
                    },
                    "temperature": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 2.0,
                        "description": "Model temperature (default: 0.7)"
                    }
                },
                "required": ["prompt"]
            }
        })
        
        # System status tool
        tools.append({
            "name": "system_status",
            "description": "Get AI team status, memory usage, and active model",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        })
        
        # Memory optimization tool
        tools.append({
            "name": "optimize_memory",
            "description": "Optimize memory usage and unload inactive models",
            "parameters": {
                "type": "object",
                "properties": {
                    "force_unload": {
                        "type": "boolean",
                        "description": "Force unload current model"
                    }
                }
            }
        })
        
        return {"tools": tools}
    
    async def handle_call_tool(self, params: Dict) -> Dict:
        """Execute a tool call with enhanced error handling"""
        tool_name = params.get("name")
        tool_params = params.get("arguments", {})
        
        try:
            if tool_name == "smart_route":
                result = await self.router.route_request(
                    tool_params.get("prompt", ""),
                    {
                        "priority": tool_params.get("priority", "normal"),
                        "temperature": tool_params.get("temperature", 0.7)
                    }
                )
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result.get("response", "")
                        }
                    ],
                    "metadata": {
                        "model_used": result.get("metadata", {}).get("model", "unknown"),
                        "member_name": result.get("metadata", {}).get("member", "unknown"),
                        "elapsed_time": result.get("metadata", {}).get("elapsed_time", 0)
                    }
                }
            
            elif tool_name.startswith("ask_"):
                member_id = tool_name.replace("ask_", "")
                if member_id in self.router.team_members:
                    # Force specific model with enhanced routing
                    old_active = self.router.active_member
                    self.router.active_member = member_id
                    
                    result = await self.router.route_request(
                        tool_params.get("prompt", ""),
                        tool_params.get("context", {})
                    )
                    
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": result.get("response", "")
                            }
                        ],
                        "metadata": {
                            "forced_model": member_id,
                            "model_name": self.router.team_members[member_id].name
                        }
                    }
                else:
                    return {"error": f"Unknown team member: {member_id}"}
            
            elif tool_name == "system_status":
                status = self.router.get_status()
                
                # Enhanced status with memory details
                enhanced_status = {
                    **status,
                    "team_members": {
                        member_id: {
                            "name": member.name,
                            "memory_gb": member.memory_gb,
                            "expertise": member.expertise[:3],
                            "performance_rating": member.performance_rating
                        }
                        for member_id, member in self.router.team_members.items()
                    }
                }
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(enhanced_status, indent=2)
                        }
                    ]
                }
            
            elif tool_name == "optimize_memory":
                force_unload = tool_params.get("force_unload", False)
                
                if force_unload and self.router.active_member:
                    member = self.router.team_members[self.router.active_member]
                    await self.router._unload_model(member.model_id)
                    self.router.active_member = None
                    message = "Force unloaded active model"
                else:
                    message = "Memory optimization completed"
                
                status = self.router.get_status()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"{message}\n\nCurrent status:\n{json.dumps(status['system'], indent=2)}"
                        }
                    ]
                }
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def handle_chat(self, params: Dict) -> Dict:
        """Handle chat request with enhanced routing"""
        messages = params.get("messages", [])
        if messages:
            prompt = messages[-1].get("content", "")
        else:
            prompt = params.get("prompt", "")
            
        result = await self.router.route_request(prompt, {"tool": "mcp_chat"})
        return {
            "content": result.get("response", ""),
            "metadata": result.get("metadata", {})
        }
    
    async def run_server(self):
        """Run the enhanced MCP server"""
        logger.info("Enhanced MCP Server starting...")
        logger.info(f"Available models: {list(self.router.team_members.keys())}")
        
        while True:
            try:
                # Read request from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                request = json.loads(line)
                response = await self.handle_request(request)
                
                # Write response to stdout
                print(json.dumps(response))
                sys.stdout.flush()
                
            except KeyboardInterrupt:
                logger.info("MCP Server shutting down...")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                error_response = {"error": str(e)}
                print(json.dumps(error_response))
                sys.stdout.flush()

if __name__ == "__main__":
    server = MCPServer()
    asyncio.run(server.run_server())
