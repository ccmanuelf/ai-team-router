#!/usr/bin/env python3
"""
Fix Web Search Tool Integration
Add tools to Ollama API calls in router
"""

def check_router_tool_integration():
    """Check how router makes Ollama calls"""
    print("Checking route_request method...")
    
    # Look for where router calls Ollama
    # Need to add tools array to API calls

def main():
    print("ISSUE: Router makes Ollama calls without tools array")
    print("FIX: Add tools parameter to Ollama API requests")
    print("\nExample fix needed:")
    print("""
    # Current (broken):
    payload = {
        "model": model_id,
        "prompt": prompt,
        "stream": False
    }
    
    # Fixed (with tools):
    payload = {
        "model": model_id, 
        "prompt": prompt,
        "stream": False,
        "tools": self._get_available_tools()
    }
    """)

if __name__ == "__main__":
    main()
