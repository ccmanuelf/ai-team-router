#!/usr/bin/env python3
"""
Generate the complete AI Team Router file
"""

def generate_router():
    """Generate complete router code"""
    
    # Write the router to file
    with open('/Users/mcampos.cerda/Documents/Programming/ai/ai_team_router.py', 'w') as f:
        f.write('''#!/usr/bin/env python3
"""AI Team Router - Complete Implementation"""

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

import aiohttp
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

# System detection
IS_M3_PRO = "Apple M3 Pro" in os.popen("system_profiler SPHardwareDataType 2>/dev/null | grep Chip").read()
TOTAL_MEMORY_GB = psutil.virtual_memory().total / (1024 ** 3)
MEMORY_OVERHEAD_GB = 4.0 if IS_M3_PRO else 2.0
MEMORY_SAFETY_BUFFER_GB = 5.0 if IS_M3_PRO else 3.0
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

class AITeamRouter:
    def __init__(self):
        self.active_member = None
        self.team_members = self._initialize_team()
        self.request_history = []
        self.performance_metrics = {}
        self.emergency_mode = False
        self.min_system_memory_gb = 2.0
        logger.info(f"Router initialized with {len(self.team_members)} members")
    
    def _initialize_team(self):
        return {
            "deepcoder_primary": TeamMember(
                name="DeepCoder Prime",
                model_id="deepcoder:latest",
                memory_gb=9.0,
                context_tokens=32768,
                roles=[TeamRole.SENIOR_ENGINEER, TeamRole.ARCHITECT],
                expertise=["vuejs", "react", "python", "refactoring"],
                special_abilities={"code_generation": "expert"},
                performance_rating=9
            ),
            "qwen_analyst": TeamMember(
                name="Qwen Data Master",
                model_id="qwen2.5:14b",
                memory_gb=9.0,
                context_tokens=32768,
                roles=[TeamRole.DATA_SCIENTIST, TeamRole.ANALYST],
                expertise=["excel", "vba", "pandas", "150k_rows"],
                special_abilities={"excel_optimization": "expert"},
                performance_rating=9
            ),
            "deepseek_legacy": TeamMember(
                name="DeepSeek Legacy",
                model_id="deepseek-coder-v2:16b",
                memory_gb=8.9,
                context_tokens=128000,
                roles=[TeamRole.SENIOR_ENGINEER],
                expertise=["laravel", "php", "338_languages"],
                special_abilities={"language_support": 338},
                performance_rating=8
            ),
            "granite_enterprise": TeamMember(
                name="Granite Enterprise",
                model_id="granite3.3:8b",
                memory_gb=4.9,
                context_tokens=4096,
                roles=[TeamRole.ENTERPRISE_SPECIALIST],
                expertise=["enterprise", "production_reports"],
                special_abilities={"enterprise_patterns": "expert"},
                performance_rating=7
            ),
            "granite_vision": TeamMember(
                name="Granite Vision",
                model_id="granite3.2-vision:2b",
                memory_gb=2.4,
                context_tokens=4096,
                roles=[TeamRole.VISION_SPECIALIST],
                expertise=["ocr", "screenshots", "image_analysis"],
                special_abilities={"vision": True},
                performance_rating=8
            ),
            "mistral_versatile": TeamMember(
                name="Mistral Versatile",
                model_id="mistral:latest",
                memory_gb=4.4,
                context_tokens=8192,
                roles=[TeamRole.JUNIOR_ENGINEER, TeamRole.DOCUMENTARIAN],
                expertise=["general", "documentation"],
                special_abilities={"versatility": "high"},
                performance_rating=7
            ),
            "gemma_medium": TeamMember(
                name="Gemma Medium",
                model_id="gemma3:4b",
                memory_gb=3.3,
                context_tokens=8192,
                roles=[TeamRole.JUNIOR_ENGINEER],
                expertise=["general", "quick_tasks"],
                special_abilities={"speed": "fast"},
                performance_rating=6
            ),
            "granite_moe": TeamMember(
                name="Granite MoE",
                model_id="granite3.1-moe:3b",
                memory_gb=2.0,
                context_tokens=4096,
                roles=[TeamRole.JUNIOR_ENGINEER],
                expertise=["efficient", "quick_responses"],
                special_abilities={"mixture_of_experts": True},
                performance_rating=6
            ),
            "gemma_tiny": TeamMember(
                name="Gemma Tiny",
                model_id="gemma3:1b",
                memory_gb=0.8,
                context_tokens=8192,
                roles=[TeamRole.JUNIOR_ENGINEER],
                expertise=["simple_tasks", "quick_responses"],
                special_abilities={"minimal_memory": True},
                performance_rating=5
            ),
            "deepseek_abliterated": TeamMember(
                name="DeepSeek Uncensored",
                model_id="huihui_ai/deepseek-r1-abliterated:latest",
                memory_gb=5.0,
                context_tokens=32768,
                roles=[TeamRole.SENIOR_ENGINEER],
                expertise=["uncensored", "research"],
                special_abilities={"uncensored": True},
                performance_rating=8,
                is_abliterated=True
            ),
            "dolphin_abliterated": TeamMember(
                name="Dolphin Uncensored",
                model_id="huihui_ai/dolphin3-abliterated:latest",
                memory_gb=4.9,
                context_tokens=32768,
                roles=[TeamRole.SENIOR_ENGINEER],
                expertise=["uncensored", "creative"],
                special_abilities={"uncensored": True},
                performance_rating=7,
                is_abliterated=True
            )
        }
    
    def _get_available_memory_gb(self):
        mem = psutil.virtual_memory()
        available = mem.available / (1024 ** 3)
        if IS_M3_PRO and mem.percent > 60:
            available *= 0.85
        return available
    
    async def _unload_model(self, model_id):
        try:
            logger.info(f"Unloading: {model_id}")
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f"{OLLAMA_API_BASE}/api/generate",
                    json={"model": model_id, "keep_alive": 0}
                )
            await asyncio.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Unload error: {e}")
            return False
    
    def _analyze_task(self, prompt, context):
        return {
            "complexity": self._estimate_complexity(prompt),
            "domain": self._identify_domain(prompt, context),
            "needs_vision": "image" in prompt.lower() or "screenshot" in prompt.lower(),
            "needs_uncensored": "uncensored" in prompt.lower(),
            "needs_large_context": len(prompt) > 3000,
            "needs_338_languages": "php" in prompt.lower() or "laravel" in prompt.lower(),
            "tool_requirements": {},
            "priority": context.get("priority", "normal")
        }
    
    def _estimate_complexity(self, prompt):
        score = 3
        if "simple" in prompt.lower():
            score -= 1
        if "complex" in prompt.lower() or "refactor" in prompt.lower():
            score += 2
        if len(prompt) > 1000:
            score += 1
        return max(1, min(5, score))
    
    def _identify_domain(self, prompt, context):
        prompt_lower = prompt.lower()
        if "vue" in prompt_lower or "react" in prompt_lower:
            return "coding"
        if "laravel" in prompt_lower or "php" in prompt_lower:
            return "coding"
        if "excel" in prompt_lower or "vba" in prompt_lower or "150k" in prompt_lower:
            return "enterprise"
        if "data" in prompt_lower or "pandas" in prompt_lower:
            return "data"
        if "image" in prompt_lower or "screenshot" in prompt_lower:
            return "visual"
        return "coding"
    
    def select_team_member(self, requirements):
        available_memory = self._get_available_memory_gb()
        logger.info(f"Selecting with {available_memory:.2f}GB available")
        
        candidate_scores = {}
        
        for member_id, member in self.team_members.items():
            required_memory = member.memory_gb + MEMORY_OVERHEAD_GB
            if available_memory < required_memory:
                continue
            
            score = 0
            
            if requirements["domain"] == "coding":
                if member_id == "deepcoder_primary":
                    score += 10
            elif requirements["domain"] == "enterprise":
                if member_id == "qwen_analyst":
                    score += 12
            elif requirements["domain"] == "visual":
                if member_id == "granite_vision":
                    score += 15
            
            if requirements["needs_uncensored"] and member.is_abliterated:
                score += 8
            
            score += member.performance_rating * 0.5
            
            candidate_scores[member_id] = score
        
        if not candidate_scores:
            return "gemma_tiny", self.team_members["gemma_tiny"]
        
        best_member_id = max(candidate_scores, key=candidate_scores.get)
        return best_member_id, self.team_members[best_member_id]
    
    async def route_request(self, prompt, context=None):
        start_time = time.time()
        context = context or {}
        
        try:
            requirements = self._analyze_task(prompt, context)
            member_id, member = self.select_team_member(requirements)
            
            if self.active_member and self.active_member != member_id:
                await self._unload_model(self.team_members[self.active_member].model_id)
            
            self.active_member = member_id
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{OLLAMA_API_BASE}/api/generate",
                    json={
                        "model": member.model_id,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": context.get("temperature", 0.7),
                            "num_ctx": min(member.context_tokens, 32768)
                        }
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        elapsed = time.time() - start_time
                        return {
                            "response": result.get("response", ""),
                            "metadata": {
                                "model": member.model_id,
                                "member": member.name,
                                "elapsed_time": elapsed,
                                "requirements": requirements
                            }
                        }
        except Exception as e:
            logger.error(f"Error: {e}")
            return {"response": "Error occurred", "metadata": {"error": str(e)}}
    
    def get_status(self):
        mem = psutil.virtual_memory()
        return {
            "active_member": self.active_member,
            "team_size": len(self.team_members),
            "system": {
                "platform": "M3 Pro" if IS_M3_PRO else "Standard",
                "total_memory_gb": TOTAL_MEMORY_GB,
                "available_memory_gb": self._get_available_memory_gb(),
                "memory_pressure": mem.percent
            }
        }

# FastAPI app
app = FastAPI(title="AI Team Router", version="1.0.0")
router = AITeamRouter()

class ChatRequest(BaseModel):
    prompt: str
    context: Dict = {}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    result = await router.route_request(request.prompt, request.context)
    return JSONResponse(content=result)

@app.get("/api/team/status")
async def get_status():
    return JSONResponse(content=router.get_status())

@app.get("/api/team/members")
async def get_members():
    members = {}
    for member_id, member in router.team_members.items():
        members[member_id] = {
            "name": member.name,
            "model_id": member.model_id,
            "memory_gb": member.memory_gb,
            "context_tokens": member.context_tokens,
            "roles": [role.value for role in member.roles],
            "expertise": member.expertise,
            "performance_rating": member.performance_rating,
            "is_abliterated": member.is_abliterated
        }
    return JSONResponse(content=members)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    return {
        "name": "AI Team Router",
        "version": "1.0.0",
        "models": len(router.team_members),
        "endpoints": {
            "chat": "POST /api/chat",
            "status": "GET /api/team/status",
            "members": "GET /api/team/members",
            "health": "GET /health"
        }
    }

if __name__ == "__main__":
    logger.info(f"Starting AI Team Router on port 11435...")
    uvicorn.run(app, host="0.0.0.0", port=11435)
''')
    
    print("✅ Router file created successfully")
    return True

if __name__ == "__main__":
    generate_router()
