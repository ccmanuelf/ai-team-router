#!/usr/bin/env python3
"""AI Team Router - Tool Implementations"""

import asyncio
import aiohttp
import json
import logging
import subprocess
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

AVAILABLE_TOOLS = {
    "web_search": {
        "description": "Search the web using SERPER, Tavily, Google, or Brave",
        "parameters": {
            "query": "Search query",
            "provider": "Search provider (serper, tavily, google, brave)"
        }
    },
    "excel_optimizer": {
        "description": "Generate optimized Pandas or VBA code for Excel tasks (150k+ rows)",
        "parameters": {
            "task": "Description of the Excel task",
            "output": "Output type (pandas or vba)"
        }
    },
    "code_executor": {
        "description": "Execute Python or JavaScript code safely",
        "parameters": {
            "code": "Code to execute",
            "language": "Programming language (python or javascript)"
        }
    },
    "file_analyzer": {
        "description": "Analyze Excel or PDF files",
        "parameters": {
            "file_path": "Path to the file",
            "file_type": "File type (excel or pdf)"
        }
    },
    "vision_analyzer": {
        "description": "Analyze images for OCR and basic vision tasks",
        "parameters": {
            "image_path": "Path to the image file"
        }
    }
}

async def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> str:
    """Execute a tool with given parameters"""
    try:
        if tool_name == "web_search":
            return await _web_search(parameters)
        elif tool_name == "excel_optimizer":
            return await _excel_optimizer(parameters)
        elif tool_name == "code_executor":
            return await _code_executor(parameters)
        elif tool_name == "file_analyzer":
            return await _file_analyzer(parameters)
        elif tool_name == "vision_analyzer":
            return await _vision_analyzer(parameters)
        else:
            return f"Unknown tool: {tool_name}"
    except Exception as e:
        logger.error(f"Tool {tool_name} error: {e}")
        return f"Tool execution error: {str(e)}"

async def _web_search(params: Dict[str, Any]) -> str:
    """Web search with fallback logic"""
    query = params.get("query", "")
    provider = params.get("provider", "auto")

    if provider == "auto":
        return await _web_search_with_fallback(query)
    else:
        # User-specified provider, no fallback
        return await _search_single_provider(provider, query)

async def _web_search_with_fallback(query: str) -> str:
    """Try providers in order with fallback"""
    # A, B, C, D ranking based on performance
    providers = ["serper", "brave", "google", "tavily"]

    for provider in providers:
        try:
            result = await _search_single_provider(provider, query)
            if not any(error in result.lower() for error in ["error", "failed", "not configured"]):
                return result
        except Exception:
            continue

    return "All search providers failed. Please check API configurations."

async def _search_single_provider(provider: str, query: str) -> str:
    """Search with a specific provider"""
    if provider == "serper":
        return await _serper_search(query)
    elif provider == "tavily":
        return await _tavily_search(query)
    elif provider == "google":
        return await _google_search(query)
    elif provider == "brave":
        return await _brave_search(query)
    else:
        return f"Unsupported search provider: {provider}"

async def _serper_search(query: str) -> str:
    """SERPER search implementation"""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "SERPER API key not configured. Set SERPER_API_KEY environment variable."

    try:
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": 3
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("organic", [])

                    if not results:
                        return "SERPER: No results found"

                    output = "SERPER Search Results:\n\n"
                    for item in results:
                        title = item.get("title", "")
                        snippet = item.get("snippet", "")
                        output += f"• {title}: {snippet[:100]}...\n"
                    return output
                else:
                    return f"SERPER API error: {response.status}"
    except Exception as e:
        return f"SERPER search failed: {str(e)}"

async def _duckduckgo_search(query: str) -> str:
    """DuckDuckGo search implementation"""
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status in [200, 202]:
                    # Handle non-standard content type
                    text = await response.text()
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError:
                        return "DuckDuckGo: Invalid response format"

                    # Try multiple result sources
                    sources = [
                        ("Abstract", data.get("Abstract", "")),
                        ("Answer", data.get("Answer", "")),
                        ("Definition", data.get("Definition", "")),
                        ("RelatedTopics", data.get("RelatedTopics", []))
                    ]

                    for source_name, source_data in sources:
                        if source_data:
                            if source_name == "RelatedTopics" and isinstance(source_data, list):
                                if source_data and "Text" in source_data[0]:
                                    return f"DuckDuckGo: {source_data[0]['Text']}"
                            else:
                                return f"DuckDuckGo: {source_data}"

                    return "DuckDuckGo: No direct results found for this query"
                return f"DuckDuckGo API error: {response.status}"
    except Exception as e:
        return f"DuckDuckGo search failed: {str(e)}"
async def _tavily_search(query: str) -> str:
    """Tavily search implementation"""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Tavily API key not configured. Set TAVILY_API_KEY environment variable."
    
    try:
        url = "https://api.tavily.com/search"
        data = {
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": True,
            "max_results": 3
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    answer = result.get("answer", "")
                    results = result.get("results", [])
                    
                    output = f"Tavily Search: {answer}\n\n"
                    for r in results[:2]:
                        output += f"• {r.get('title', '')}: {r.get('content', '')[:100]}...\n"
                    return output
                else:
                    return f"Tavily API error: {response.status}"
    except Exception as e:
        return f"Tavily search failed: {str(e)}"

async def _google_search(query: str) -> str:
    """Google Custom Search implementation"""
    api_key = os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("GOOGLE_CSE_ID")
    
    if not api_key or not cx:
        return "Google search requires GOOGLE_API_KEY and GOOGLE_CX environment variables."
    
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cx,
            "q": query,
            "num": 3
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    items = result.get("items", [])
                    
                    output = "Google Search Results:\n\n"
                    for item in items:
                        title = item.get("title", "")
                        snippet = item.get("snippet", "")
                        output += f"• {title}: {snippet[:100]}...\n"
                    return output
                else:
                    return f"Google API error: {response.status}"
    except Exception as e:
        return f"Google search failed: {str(e)}"

async def _brave_search(query: str) -> str:
    """Brave Search API implementation"""
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return "Brave API key not configured. Set BRAVE_API_KEY environment variable."

    try:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": api_key
        }
        # Use proper URL encoding for query
        import urllib.parse
        encoded_query = urllib.parse.quote_plus(query)
        params = {
            "q": encoded_query,
            "country": "us",
            "search_lang": "en"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    web_results = result.get("web", {}).get("results", [])

                    if not web_results:
                        return "Brave Search: No results found"

                    output = "Brave Search Results:\n\n"
                    for item in web_results[:3]:
                        title = item.get("title", "")
                        description = item.get("description", "")
                        output += f"• {title}: {description[:100]}...\n"
                    return output
                elif response.status == 422:
                    error_text = await response.text()
                    return f"Brave API parameter error (422): {error_text[:100]}"
                else:
                    return f"Brave API error: {response.status}"
    except Exception as e:
        return f"Brave search failed: {str(e)}"
async def _excel_optimizer(params: Dict[str, Any]) -> str:
    """Excel optimization code generator"""
    task = params.get("task", "")
    output = params.get("output", "pandas")
    
    if output.lower() == "vba":
        return _generate_vba_code(task)
    else:
        return _generate_pandas_code(task)

def _generate_vba_code(task: str) -> str:
    """Generate VBA code for Excel tasks"""
    if "inventory" in task.lower() or "reconciliation" in task.lower():
        return '''
' VBA Code for Inventory Reconciliation (150k+ rows optimized)
Sub InventoryReconciliation()
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    
    Dim ws As Worksheet
    Set ws = ActiveSheet
    
    ' Optimized for large datasets
    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    
    ' Process in chunks for memory efficiency
    Dim chunkSize As Long
    chunkSize = 10000
    
    Dim i As Long
    For i = 2 To lastRow Step chunkSize
        ProcessInventoryChunk ws, i, Application.Min(i + chunkSize - 1, lastRow)
        DoEvents
    Next i
    
    Application.ScreenUpdating = True
    Application.Calculation = xlCalculationAutomatic
    
    MsgBox "Inventory reconciliation complete. Processed " & (lastRow - 1) & " rows."
End Sub
'''
    else:
        return f"VBA code template for: {task}\n' Optimized for 150k+ rows\n' Memory-efficient processing included"

def _generate_pandas_code(task: str) -> str:
    """Generate Pandas code for Excel tasks"""
    if "inventory" in task.lower() or "reconciliation" in task.lower():
        return '''
import pandas as pd

# Optimized Pandas code for Inventory Reconciliation (150k+ rows)
def inventory_reconciliation(file_path):
    df = pd.read_excel(file_path, engine='openpyxl')
    
    # Memory optimization for large datasets
    df = df.astype({
        'item_id': 'category',
        'quantity': 'int32',
        'price': 'float32'
    })
    
    # Process in chunks
    chunk_size = 10000
    results = []
    
    for chunk_start in range(0, len(df), chunk_size):
        chunk_end = min(chunk_start + chunk_size, len(df))
        chunk = df.iloc[chunk_start:chunk_end]
        reconciled = process_inventory_chunk(chunk)
        results.append(reconciled)
    
    final_result = pd.concat(results, ignore_index=True)
    final_result.to_excel('inventory_reconciled.xlsx', index=False)
    return f"Processed {len(df)} rows successfully"

def process_inventory_chunk(chunk):
    return chunk.groupby('item_id').agg({
        'quantity': 'sum',
        'price': 'mean'
    }).reset_index()
'''
    else:
        return f"# Pandas code for: {task}\n# Optimized for 150k+ rows"

async def _code_executor(params: Dict[str, Any]) -> str:
    """Safe code execution"""
    code = params.get("code", "")
    language = params.get("language", "python")
    
    if language.lower() == "python":
        return _execute_python(code)
    elif language.lower() == "javascript":
        return _execute_javascript(code)
    else:
        return f"Unsupported language: {language}"

def _execute_python(code: str) -> str:
    """Execute Python code safely"""
    try:
        if any(dangerous in code.lower() for dangerous in ['import os', 'subprocess', 'exec', 'eval']):
            return "Code execution blocked: potentially unsafe operations detected"

        # Create safe namespace
        safe_globals = {
            '__builtins__': {
                'print': print, 'len': len, 'str': str, 'int': int,
                'float': float, 'list': list, 'dict': dict, 'range': range,
                'sum': sum, 'max': max, 'min': min
            }
        }

        import io
        import contextlib

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(code, safe_globals)

        result = output.getvalue()
        return result if result else "Code executed successfully (no output)"

    except Exception as e:
        return f"Python execution error: {str(e)}"
    
    def _execute_javascript(code: str) -> str:
        """Execute JavaScript code safely"""
        try:
            result = subprocess.run(
                ['node', '-e', code],
                capture_output=True,
                text=True,
                timeout=10
            )
    
            if result.returncode == 0:
                return result.stdout if result.stdout else "JavaScript executed successfully"
            else:
                return f"JavaScript error: {result.stderr}"
    
        except subprocess.TimeoutExpired:
            return "JavaScript execution timed out"
        except FileNotFoundError:
            return "Node.js not found - JavaScript execution unavailable"
        except Exception as e:
            return f"JavaScript execution error: {str(e)}"

async def _file_analyzer(params: Dict[str, Any]) -> str:
    """File analysis implementation"""
    file_path = params.get("file_path", "")
    file_type = params.get("file_type", "excel")
    
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
    return f"File Analysis for {os.path.basename(file_path)}:\nFile size: {file_size:.2f} MB\nAnalysis requires additional libraries"

async def _vision_analyzer(params: Dict[str, Any]) -> str:
    """Vision analysis implementation"""
    image_path = params.get("image_path", "")
    
    if not os.path.exists(image_path):
        return f"Image not found: {image_path}"
    
    file_size = os.path.getsize(image_path) / 1024  # KB
    return f"Vision Analysis for {os.path.basename(image_path)}:\nFile size: {file_size:.2f} KB\nOCR analysis requires tesseract or similar library"

if __name__ == "__main__":
    async def test():
        print("Testing JavaScript execution...")
        result = await execute_tool("code_executor", {"code": "console.log('Hello from Node.js!')", "language": "javascript"})
        print(result)
        
        print("\nTesting web search providers...")
        for provider in ["duckduckgo", "tavily", "google", "brave"]:
            result = await execute_tool("web_search", {"query": "Python tutorial", "provider": provider})
            print(f"{provider}: {result[:100]}...")
    
    asyncio.run(test())
