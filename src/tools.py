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


if __name__ == "__main__":
    # Test the tools
    import asyncio
    
    async def test():
        print("Testing Web Search...")
        result = await execute_tool("web_search", {"query": "Python pandas tutorial", "provider": "duckduckgo"})
        print(result[:200])
        
        print("\nTesting Excel Optimizer...")
        result = await execute_tool("excel_optimizer", {"task": "inventory reconciliation for 150000 rows", "output": "pandas"})
        print(result[:500])
        
        print("\nTesting VBA Generator...")
        result = await execute_tool("excel_optimizer", {"task": "production report with 150k rows", "output": "vba"})
        print(result[:500])
    
    asyncio.run(test())
