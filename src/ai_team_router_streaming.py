#!/usr/bin/env python3
"""AI Team Router - Phase 4C Production with Streaming Enhancement"""

import os
import sys
import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# PHASE 4C: Enhanced with streaming for complex tasks
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import psutil
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Logging setup
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/router.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# System detection with aggressive memory management for local AI
IS_M3_PRO = "Apple M3 Pro" in os.popen("system_profiler SPHardwareDataType 2>/dev/null | grep Chip").read()
TOTAL_MEMORY_GB = psutil.virtual_memory().total / (1024 ** 3)

# AGGRESSIVE: Minimal overhead for maximum model access - prioritize functionality over speed
MEMORY_OVERHEAD_GB = 0.5 if IS_M3_PRO else 0.3  # Reduced from 1.5/1.0
MEMORY_SAFETY_BUFFER_GB = 0.5 if IS_M3_PRO else 0.3  # Reduced from 1.0/0.5
MEMORY_EDGE_MODE = True  # Allow over-edge operation with warnings
MEMORY_EDGE_LIMIT_GB = 4.0  # Allow up to 4GB over-memory
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

class TeamRole(Enum):
    SENIOR_ENGINEER = "senior_engineer"
    JUNIOR_ENGINEER = "junior_engineer"
    DATA_SCIENTIST = "data_scientist"
    ARCHITECT = "architect"
    ANALYST = "analyst"
    DOCUMENTARIAN = "documentarian"
    VISION_SPECIALIST = "vision_specialist"
    ENTERPRISE_SPECIALIST = "enterprise_specialist"

@dataclass
class TeamMember:
    name: str
    model_id: str
    memory_gb: float
    context_tokens: int
    roles: List[TeamRole]
    expertise: List[str]
    special_abilities: Dict[str, Any]
    performance_rating: int
    is_abliterated: bool = False
    tool_integration: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.tool_integration is None:
            self.tool_integration = {
                "web_search": True,
                "code_execution": True,
                "file_analysis": True,
                "excel_optimizer": True,
                "vision": "vision" in self.model_id.lower()
            }

class OptimizedHTTPClient:
    """Optimized HTTP client for Ollama connections - Phase 4C with Streaming"""
    
    def __init__(self, base_url="http://localhost:11434", max_retries=2):
        self.base_url = base_url
        self.session = self._create_optimized_session(max_retries)
        
    def _create_optimized_session(self, max_retries):
        """Create session with optimized connection settings"""
        session = requests.Session()
    
        # Configure retry strategy (Phase 4A proven configuration)
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=0.5  # 0.5s exponential backoff
        )        
        
        # Configure HTTP adapter with connection pooling (Phase 4A validated)
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=5,    # Phase 4A optimized
            pool_maxsize=10,       # Phase 4A optimized
            pool_block=False       # Non-blocking
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers (Phase 4A proven)
        session.headers.update({
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'User-Agent': 'AI-Team-Router-Phase4C/1.0'
        })
        
        return session
    
    def generate(self, model_id, prompt, timeout=600, stream=False, options=None):
        """Send generation request with Phase 4A proven error handling"""
        
        payload = {
            "model": model_id,
            "prompt": prompt,
            "stream": stream,
            "options": options or {}
        }
        
        start_time = time.time()
        
        try:
            logger.info(f"HTTP Request: {model_id} (timeout: {timeout}s)")
            
            # Use requests instead of aiohttp (Phase 4A proven fix)
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout,
                stream=False
            )
            
            connection_time = time.time() - start_time
            logger.info(f"HTTP response received in {connection_time:.1f}s")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    total_time = time.time() - start_time
                    logger.info(f"✅ Request completed in {total_time:.1f}s")
                    return {
                        "success": True,
                        "response": result.get("response", ""),
                        "response_time": total_time,
                        "connection_time": connection_time,
                        "method": "non_streaming"
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    return {
                        "success": False,
                        "error": f"JSON decode error: {e}",
                        "response_time": time.time() - start_time
                    }
            else:
                logger.error(f"HTTP error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": time.time() - start_time
                }
                
        except requests.exceptions.Timeout as e:
            total_time = time.time() - start_time
            logger.error(f"Request timeout after {total_time:.1f}s: {e}")
            return {
                "success": False,
                "error": f"Timeout after {total_time:.1f}s: {e}",
                "response_time": total_time
            }
        except requests.exceptions.ConnectionError as e:
            total_time = time.time() - start_time
            logger.error(f"Connection error after {total_time:.1f}s: {e}")
            return {
                "success": False,
                "error": f"Connection error: {e}",
                "response_time": total_time
            }
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Unexpected error after {total_time:.1f}s: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {e}",
                "response_time": total_time
            }
    
    def generate_streaming(self, model_id, prompt, no_token_timeout=180, options=None):
        """Send streaming generation request with intelligent timeout - Phase 4C Enhancement"""
        
        payload = {
            "model": model_id,
            "prompt": prompt,
            "stream": True,
            "options": options or {}
        }
        
        start_time = time.time()
        last_token_time = start_time
        
        try:
            logger.info(f"🌊 STREAMING Request: {model_id} (no-token timeout: {no_token_timeout}s)")
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30,  # Connection timeout only
                stream=True
            )
            
            if response.status_code != 200:
                logger.error(f"HTTP error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": time.time() - start_time
                }
            
            # Stream processing with intelligent timeout
            full_response = ""
            chunk_count = 0
            total_timeout = 900  # 15 minute absolute maximum
            
            logger.info(f"📡 Streaming started...")
            
            for line in response.iter_lines():
                current_time = time.time()
                total_elapsed = current_time - start_time
                time_since_token = current_time - last_token_time
                
                # Absolute timeout check
                if total_elapsed > total_timeout:
                    logger.warning(f"⏰ ABSOLUTE TIMEOUT: {total_elapsed:.1f}s")
                    return {
                        "success": False,
                        "error": f"Absolute timeout after {total_elapsed:.1f}s",
                        "response_time": total_elapsed,
                        "chunks_received": chunk_count,
                        "partial_response": full_response
                    }
                
                # No-token timeout check
                if time_since_token > no_token_timeout:
                    logger.warning(f"⏰ NO-TOKEN TIMEOUT: {time_since_token:.1f}s since last token")
                    return {
                        "success": False,
                        "error": f"No tokens for {time_since_token:.1f}s",
                        "response_time": total_elapsed,
                        "chunks_received": chunk_count,
                        "partial_response": full_response
                    }
                
                if line:
                    last_token_time = current_time
                    chunk_count += 1
                    
                    # Progress indicator
                    if chunk_count % 500 == 0:
                        logger.info(f"📦 {chunk_count} chunks ({total_elapsed:.1f}s elapsed)")
                    
                    try:
                        chunk_data = json.loads(line)
                        if "response" in chunk_data:
                            full_response += chunk_data["response"]
                        
                        # Check if done
                        if chunk_data.get("done", False):
                            elapsed = current_time - start_time
                            logger.info(f"✅ STREAMING SUCCESS: {elapsed:.1f}s")
                            logger.info(f"📊 Response: {len(full_response)} chars, {chunk_count} chunks")
                            
                            return {
                                "success": True,
                                "response": full_response,
                                "response_time": elapsed,
                                "chunks": chunk_count,
                                "method": "streaming"
                            }
                            
                    except json.JSONDecodeError:
                        continue  # Skip invalid JSON
            
            # Stream ended without done=True
            elapsed = time.time() - start_time
            logger.warning(f"⚠️ Stream ended unexpectedly: {elapsed:.1f}s")
            return {
                "success": False,
                "error": "Stream ended unexpectedly",
                "response_time": elapsed,
                "chunks_received": chunk_count,
                "partial_response": full_response
            }
            
        except requests.exceptions.Timeout as e:
            total_time = time.time() - start_time
            logger.error(f"Streaming connection timeout after {total_time:.1f}s: {e}")
            return {
                "success": False,
                "error": f"Connection timeout: {e}",
                "response_time": total_time
            }
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Streaming error after {total_time:.1f}s: {e}")
            return {
                "success": False,
                "error": f"Streaming error: {e}",
                "response_time": total_time
            }
    
    def unload(self, model_id, timeout=30):
        """Send unload request"""
        return self.generate(
            model_id=model_id,
            prompt="",
            timeout=timeout,
            options={"keep_alive": 0}
        )
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()
