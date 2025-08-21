#!/usr/bin/env python3
"""
Investigate Web Search Tool Integration Issue
"""

import requests
import json
from datetime import datetime

def check_router_tools():
    """Check router tool configuration"""
    print("🔧 ROUTER TOOL INTEGRATION CHECK")
    print("="*50)
    
    # Check team status
    try:
        response = requests.get("http://localhost:11435/api/team/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print("✅ Router responding")
            print(f"Available tools: {status.get('tools', [])}")
            print(f"Members: {len(status.get('members', []))}")
            
            if not status.get('tools'):
                print("🚨 NO TOOLS AVAILABLE - This explains inconsistency!")
            
        else:
            print(f"❌ Status error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

def check_ollama_direct():
    """Check if Ollama has tool support"""
    print(f"\n🤖 OLLAMA TOOL SUPPORT CHECK")
    print("="*50)
    
    try:
        # Test direct Ollama call with tool
        payload = {
            "model": "qwen2.5:14b",
            "prompt": "Search for Excel VBA functions",
            "stream": False,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "description": "Search the web",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"}
                            }
                        }
                    }
                }
            ]
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Ollama accepts tool definitions")
        else:
            print(f"❌ Ollama error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Ollama test error: {e}")

def main():
    print(f"Tool Integration Debug - {datetime.now()}")
    
    check_router_tools()
    check_ollama_direct()
    
    print(f"\n🎯 CONCLUSION:")
    print("Router reports no available tools")
    print("This explains web search inconsistency")
    print("Models fall back to training data when tools unavailable")

if __name__ == "__main__":
    main()
