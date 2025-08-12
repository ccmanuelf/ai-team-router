#!/usr/bin/env python3
"""
Chroma Vector Database Integration for AI Team Router
Provides persistent memory and context management
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️  Chroma not installed. Run: pip install chromadb")

class ChromaMemory:
    """Vector database for AI Team Router memory and context"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize Chroma database"""
        if not CHROMA_AVAILABLE:
            raise ImportError("Chroma is not installed. Run: pip install chromadb")
        
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collections
        self.collections = {
            "conversations": self._get_or_create_collection("conversations"),
            "code_snippets": self._get_or_create_collection("code_snippets"),
            "documentation": self._get_or_create_collection("documentation"),
            "excel_patterns": self._get_or_create_collection("excel_patterns"),
            "model_performance": self._get_or_create_collection("model_performance")
        }
        
        print(f"✅ Chroma initialized at {persist_directory}")
    
    def _get_or_create_collection(self, name: str) -> Any:
        """Get or create a collection"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(
                name=name,
                metadata={"created": datetime.now().isoformat()}
            )
    
    def store_conversation(self, prompt: str, response: str, metadata: Dict[str, Any]):
        """Store a conversation in vector database"""
        conversation_id = self._generate_id(prompt)
        
        self.collections["conversations"].add(
            documents=[f"Prompt: {prompt}\nResponse: {response}"],
            metadatas=[{
                **metadata,
                "timestamp": datetime.now().isoformat(),
                "prompt_length": len(prompt),
                "response_length": len(response)
            }],
            ids=[conversation_id]
        )
        
        # Also store model performance
        if "model" in metadata:
            self.store_model_performance(
                metadata["model"],
                metadata.get("elapsed_time", 0),
                metadata.get("success", True)
            )
    
    def store_code_snippet(self, code: str, language: str, description: str, tags: List[str]):
        """Store code snippet for reuse"""
        snippet_id = self._generate_id(code)
        
        self.collections["code_snippets"].add(
            documents=[code],
            metadatas=[{
                "language": language,
                "description": description,
                "tags": ",".join(tags),
                "timestamp": datetime.now().isoformat()
            }],
            ids=[snippet_id]
        )
    
    def store_excel_pattern(self, pattern: str, use_case: str, row_count: int):
        """Store Excel/VBA patterns for large datasets"""
        pattern_id = self._generate_id(pattern)
        
        self.collections["excel_patterns"].add(
            documents=[pattern],
            metadatas=[{
                "use_case": use_case,
                "row_count": row_count,
                "optimized_for_150k": row_count >= 150000,
                "timestamp": datetime.now().isoformat()
            }],
            ids=[pattern_id]
        )
    
    def store_model_performance(self, model: str, response_time: float, success: bool):
        """Track model performance metrics"""
        perf_id = f"{model}_{datetime.now().timestamp()}"
        
        self.collections["model_performance"].add(
            documents=[f"Model: {model}, Time: {response_time}s, Success: {success}"],
            metadatas=[{
                "model": model,
                "response_time": response_time,
                "success": success,
                "timestamp": datetime.now().isoformat()
            }],
            ids=[perf_id]
        )
    
    def search_similar_conversations(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar past conversations"""
        results = self.collections["conversations"].query(
            query_texts=[query],
            n_results=n_results
        )
        
        return self._format_results(results)
    
    def search_code_snippets(self, query: str, language: Optional[str] = None, n_results: int = 5) -> List[Dict]:
        """Search for relevant code snippets"""
        where_clause = {"language": language} if language else None
        
        results = self.collections["code_snippets"].query(
            query_texts=[query],
            where=where_clause,
            n_results=n_results
        )
        
        return self._format_results(results)
    
    def search_excel_patterns(self, query: str, min_rows: Optional[int] = None, n_results: int = 5) -> List[Dict]:
        """Search for Excel patterns"""
        where_clause = {"row_count": {"$gte": min_rows}} if min_rows else None
        
        results = self.collections["excel_patterns"].query(
            query_texts=[query],
            where=where_clause,
            n_results=n_results
        )
        
        return self._format_results(results)
    
    def get_model_stats(self, model: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics for models"""
        where_clause = {"model": model} if model else None
        
        results = self.collections["model_performance"].get(
            where=where_clause,
            limit=1000
        )
        
        if not results["metadatas"]:
            return {"error": "No performance data found"}
        
        # Calculate statistics
        stats = {}
        for metadata in results["metadatas"]:
            model_name = metadata["model"]
            if model_name not in stats:
                stats[model_name] = {
                    "count": 0,
                    "total_time": 0,
                    "successes": 0,
                    "failures": 0
                }
            
            stats[model_name]["count"] += 1
            stats[model_name]["total_time"] += metadata["response_time"]
            if metadata["success"]:
                stats[model_name]["successes"] += 1
            else:
                stats[model_name]["failures"] += 1
        
        # Calculate averages
        for model_name in stats:
            s = stats[model_name]
            s["average_time"] = s["total_time"] / s["count"] if s["count"] > 0 else 0
            s["success_rate"] = s["successes"] / s["count"] * 100 if s["count"] > 0 else 0
        
        return stats
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def _format_results(self, results: Dict) -> List[Dict]:
        """Format Chroma results for easier use"""
        formatted = []
        
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted.append({
                    "document": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0
                })
        
        return formatted
    
    def reset_collection(self, collection_name: str):
        """Reset a specific collection"""
        if collection_name in self.collections:
            self.client.delete_collection(collection_name)
            self.collections[collection_name] = self._get_or_create_collection(collection_name)
            print(f"✅ Reset collection: {collection_name}")
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics for all collections"""
        stats = {}
        for name, collection in self.collections.items():
            stats[name] = collection.count()
        return stats


class ChromaIntegration:
    """Integration layer between AI Team Router and Chroma"""
    
    def __init__(self, router, chroma_dir: str = "./chroma_db"):
        """Initialize Chroma integration with router"""
        self.router = router
        self.memory = ChromaMemory(chroma_dir)
        self.context_window = 5  # Number of similar conversations to include
        print("✅ Chroma integration initialized")
    
    async def enhanced_route_request(self, prompt: str, context: Dict = None) -> Dict[str, Any]:
        """Route request with Chroma context enhancement"""
        context = context or {}
        
        # Search for similar past conversations
        similar = self.memory.search_similar_conversations(prompt, self.context_window)
        
        # Add similar context if found
        if similar:
            context["similar_conversations"] = similar
            context["has_context"] = True
        
        # Check for relevant code snippets
        code_snippets = self.memory.search_code_snippets(prompt)
        if code_snippets:
            context["relevant_code"] = code_snippets
        
        # Check for Excel patterns if needed
        if "excel" in prompt.lower() or "vba" in prompt.lower() or "150" in prompt.lower():
            excel_patterns = self.memory.search_excel_patterns(prompt, min_rows=100000)
            if excel_patterns:
                context["excel_patterns"] = excel_patterns
        
        # Route the request
        result = await self.router.route_request(prompt, context)
        
        # Store the conversation
        if result.get("response"):
            self.memory.store_conversation(
                prompt,
                result["response"],
                result.get("metadata", {})
            )
        
        # Add memory stats to response
        result["memory_stats"] = self.memory.get_collection_stats()
        
        return result
    
    def get_insights(self) -> Dict[str, Any]:
        """Get insights from stored data"""
        return {
            "collection_stats": self.memory.get_collection_stats(),
            "model_performance": self.memory.get_model_stats(),
            "total_conversations": self.memory.collections["conversations"].count(),
            "total_code_snippets": self.memory.collections["code_snippets"].count(),
            "total_excel_patterns": self.memory.collections["excel_patterns"].count()
        }


# Example usage and test
if __name__ == "__main__":
    print("=" * 70)
    print("CHROMA VECTOR DATABASE SETUP FOR AI TEAM ROUTER")
    print("=" * 70)
    
    if not CHROMA_AVAILABLE:
        print("\n❌ Chroma not installed!")
        print("Run: pip install chromadb")
        print("\nThen re-run this script to set up vector database")
    else:
        # Initialize Chroma
        memory = ChromaMemory()
        
        # Store some example data
        print("\n📝 Storing example data...")
        
        # Store a conversation
        memory.store_conversation(
            "Create a Vue component for data table",
            "Here's a Vue 3 component with TypeScript...",
            {"model": "deepcoder:latest", "elapsed_time": 4.5, "success": True}
        )
        
        # Store Excel pattern
        memory.store_excel_pattern(
            "Sub ProcessLargeDataset()\\n  Dim dataArray As Variant\\n  dataArray = Range(\\"A1:Z150000\\").Value\\nEnd Sub",
            "Process 150k rows efficiently",
            150000
        )
        
        # Store code snippet
        memory.store_code_snippet(
            "const DataTable = () => { return <table>...</table> }",
            "javascript",
            "React data table component",
            ["react", "table", "component"]
        )
        
        print("✅ Example data stored")
        
        # Show statistics
        print("\n📊 Collection Statistics:")
        stats = memory.get_collection_stats()
        for name, count in stats.items():
            print(f"   {name}: {count} items")
        
        # Test search
        print("\n🔍 Testing search...")
        results = memory.search_similar_conversations("Vue component")
        print(f"   Found {len(results)} similar conversations")
        
        print("\n✅ Chroma setup complete!")
        print("\n📁 Data stored in: ./chroma_db/")
        print("📚 Collections created:")
        print("   - conversations (stores all interactions)")
        print("   - code_snippets (reusable code)")
        print("   - excel_patterns (150k+ row solutions)")
        print("   - model_performance (metrics)")
        print("   - documentation (reference docs)")
