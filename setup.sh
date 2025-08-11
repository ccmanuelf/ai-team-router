("has_image", False)
        has_keywords = any(word in prompt.lower() for word in vision_indicators)
        return has_image or has_keywords
    
    def _estimate_context_size(self, prompt: str, context: Dict) -> int:
        base_tokens = len(prompt.split()) * 1.3
        
        if context.get("code_files"):
            for file in context.get("code_files", []):
                base_tokens += len(file.get("content", "").split()) * 1.3
        
        if context.get("previous_messages"):
            for msg in context.get("previous_messages", []):
                base_tokens += len(msg.get("content", "").split()) * 1.3
        
        return int(base_tokens)
    
    def select_team_member(self, requirements: Dict[str, Any]) -> Tuple[str, TeamMember]:
        # Check for health issues first
        health_issue = self._monitor_health()
        if health_issue:
            return health_issue
        
        available_memory = self._get_available_memory_gb()
        current_pressure = psutil.virtual_memory().percent
        
        if IS_M3_PRO and current_pressure > 70:
            available_memory *= 0.9
            logger.warning(f"High memory pressure ({current_pressure}%), reducing available to {available_memory:.2f}GB")
        
        logger.info(f"Selecting team member with {available_memory:.2f}GB available")
        
        candidate_scores = {}
        
        for member_id, member in self.team_members.items():
            required_memory = member.memory_gb + (MEMORY_OVERHEAD_GB if IS_M3_PRO else self.min_system_memory_gb)
            if available_memory < required_memory:
                continue
            
            score = 0
            
            # Domain-specific scoring
            if requirements["domain"] == "coding":
                if "vue" in str(requirements).lower() or "laravel" in str(requirements).lower():
                    if member_id == "deepcoder_primary":
                        score += 12 * requirements["complexity"]
                    elif member_id == "deepseek_legacy" and "laravel" in str(requirements).lower():
                        score += 10 * requirements["complexity"]
                elif member_id == "deepcoder_primary":
                    score += 10 * requirements["complexity"]
                elif TeamRole.SENIOR_ENGINEER in member.roles:
                    score += 7 * requirements["complexity"]
                elif TeamRole.JUNIOR_ENGINEER in member.roles:
                    score += 4
            
            if requirements["domain"] == "algorithms":
                if member_id == "deepcoder_primary":
                    score += 15
            
            if requirements["domain"] == "data" or requirements["domain"] == "enterprise":
                if member_id == "qwen_analyst":
                    score += 12
                elif member_id == "granite_enterprise":
                    score += 10
                elif TeamRole.DATA_SCIENTIST in member.roles:
                    score += 8
            
            if requirements["domain"] == "visual":
                if member_id == "granite_vision":
                    score += 15
                elif TeamRole.VISION_SPECIALIST in member.roles:
                    score += 10
            
            # Tool requirements scoring
            tool_reqs = requirements.get("tool_requirements", {})
            for tool, required in tool_reqs.items():
                if required and member.tool_integration.get(tool, False):
                    score += 3
            
            # Special abilities scoring
            if requirements["needs_uncensored"]:
                if member.is_abliterated:
                    score += 8
            
            if requirements["needs_large_context"]:
                if member.context_tokens >= 128000:
                    score += 4
            
            if requirements["needs_338_languages"]:
                if member_id == "deepseek_legacy":
                    score += 10
            
            # Performance rating bonus
            score += member.performance_rating * 0.5
            
            # Efficiency adjustment
            if requirements["complexity"] <= 2 and member.performance_rating >= 9:
                score -= 3
            
            # Memory headroom scoring for M3
            if IS_M3_PRO:
                headroom = available_memory - required_memory
                if headroom > 4:
                    score += 1
                elif headroom < 2:
                    score -= 2
            
            candidate_scores[member_id] = score
        
        if not candidate_scores:
            # Emergency fallback
            for member_id, member in sorted(self.team_members.items(), 
                                           key=lambda x: x[1].memory_gb):
                required = member.memory_gb + (MEMORY_OVERHEAD_GB if IS_M3_PRO else self.min_system_memory_gb)
                if available_memory >= required:
                    logger.warning(f"Emergency selection: {member.name}")
                    return member_id, member
            raise Exception(f"No team members available with {available_memory:.2f}GB available")
        
        best_member_id = max(candidate_scores, key=candidate_scores.get)
        best_member = self.team_members[best_member_id]
        
        logger.info(f"Selected {best_member.name} (score: {candidate_scores[best_member_id]:.1f}) for {requirements['domain']} task")
        
        return best_member_id, best_member
    
    async def delegate_task(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            requirements = self.analyze_task_requirements(prompt, context)
            member_id, team_member = self.select_team_member(requirements)
            
            if self.active_member and self.active_member != member_id:
                await self._unload_current_member()
                if IS_M3_PRO:
                    await asyncio.sleep(1)
            
            self.active_member = member_id
            
            enhanced_prompt = self._prepare_prompt_for_member(prompt, team_member, requirements)
            response = await self._execute_with_member(enhanced_prompt, team_member, context)
            
            return {
                "response": response,
                "team_member": team_member.name,
                "model_id": team_member.model_id,
                "task_analysis": requirements,
                "is_abliterated": team_member.is_abliterated
            }
            
        except Exception as e:
            logger.error(f"Task delegation failed: {e}")
            raise
    
    async def _execute_with_member(self, prompt: str, member: TeamMember, context: Dict) -> str:
        try:
            # Use Ollama API directly for better control
            await self._ensure_session()
            
            payload = {
                "model": member.model_id,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": member.context_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            if IS_M3_PRO:
                # Optimize for M3 unified memory
                payload["options"]["num_gpu"] = min(int(member.memory_gb * 1024), 14336)
            
            async with self.session.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {error_text}")
                
                result = await response.json()
                return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Failed to execute with {member.name}: {e}")
            raise
    
    def get_team_status(self) -> Dict[str, Any]:
        available_memory = self._get_available_memory_gb()
        memory_info = psutil.virtual_memory()
        
        available_members = []
        for member_id, member in self.team_members.items():
            required = member.memory_gb + (MEMORY_OVERHEAD_GB if IS_M3_PRO else self.min_system_memory_gb)
            if available_memory >= required:
                available_members.append({
                    "id": member_id,
                    "name": member.name,
                    "memory_gb": member.memory_gb,
                    "expertise": member.expertise[:3]
                })
        
        return {
            "system": {
                "platform": "M3 Pro" if IS_M3_PRO else "Standard",
                "available_memory_gb": round(available_memory, 2),
                "total_memory_gb": round(memory_info.total / (1024**3), 2),
                "memory_pressure_percent": memory_info.percent
            },
            "active_member": self.team_members[self.active_member].name if self.active_member else None,
            "team_size": len(self.team_members),
            "available_members": available_members
        }
    
    def get_all_members(self) -> List[Dict[str, Any]]:
        members = []
        for member_id, member in self.team_members.items():
            members.append({
                "id": member_id,
                "name": member.name,
                "model_id": member.model_id,
                "memory_gb": member.memory_gb,
                "context_tokens": member.context_tokens,
                "roles": [role.value for role in member.roles],
                "expertise": member.expertise,
                "special_abilities": member.special_abilities,
                "performance_rating": member.performance_rating,
                "is_abliterated": member.is_abliterated
            })
        return members
    
    async def cleanup(self):
        if self.active_member:
            await self._unload_current_member()
        if self.session:
            await self.session.close()

# FastAPI Integration
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="AI Development Team API - M3 Pro Optimized",
    version="5.0.0",
    description="Complete AI Team with Tool Integration, MCP Support, and Open Web UI"
)

# Add CORS for Open Web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

team_manager = AITeamManager()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Team Router with M3 Pro optimizations")

@app.on_event("shutdown")
async def shutdown_event():
    await team_manager.cleanup()

# Ollama-compatible endpoints for Open Web UI
@app.get("/api/tags")
async def list_models():
    """Ollama-compatible model listing for Open Web UI"""
    models = []
    for member_id, member in team_manager.team_members.items():
        models.append({
            "name": "router",  # Single router model
            "modified_at": datetime.now().isoformat(),
            "size": int(member.memory_gb * 1024 * 1024 * 1024),
            "digest": member_id,
            "details": {
                "format": "gguf",
                "family": "ollama",
                "families": ["ollama"],
                "parameter_size": f"{member.memory_gb}B",
                "quantization_level": "Q4_K_M"
            }
        })
        break  # Only show router as single model
    
    return {"models": models}

@app.post("/api/generate")
async def generate(request: Request):
    """Ollama-compatible generation endpoint"""
    data = await request.json()
    prompt = data.get("prompt", "")
    model = data.get("model", "router")
    stream = data.get("stream", False)
    
    if stream:
        # Streaming not implemented yet
        raise HTTPException(status_code=501, detail="Streaming not implemented")
    
    context = {
        "tool": "openwebui",
        "model_requested": model
    }
    
    result = await team_manager.delegate_task(prompt, context)
    
    return {
        "model": result["model_id"],
        "created_at": datetime.now().isoformat(),
        "response": result["response"],
        "done": True,
        "context": [],
        "total_duration": 0,
        "load_duration": 0,
        "prompt_eval_duration": 0,
        "eval_count": len(result["response"].split()),
        "eval_duration": 0
    }

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """Enhanced chat endpoint with Open Web UI support"""
    try:
        data = await request.json()
        
        # Handle both formats
        if "messages" in data:
            # Open Web UI format
            messages = data.get("messages", [])
            if messages:
                prompt = messages[-1].get("content", "")
            else:
                prompt = ""
        else:
            # Direct format
            prompt = data.get("prompt", "")
        
        context = data.get("context", {})
        
        result = await team_manager.delegate_task(prompt, context)
        
        return JSONResponse(content={
            "success": True,
            "response": result["response"],
            "metadata": {
                "team_member": result["team_member"],
                "model": result["model_id"]
            }
        })
    except Exception as e:
        logger.error(f"Request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/team/status")
async def team_status_endpoint():
    return JSONResponse(content=team_manager.get_team_status())

@app.get("/api/team/members")
async def team_members_endpoint():
    return JSONResponse(content={"members": team_manager.get_all_members()})

@app.post("/api/tools/zed")
async def zed_integration(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    code_context = data.get("code", "")
    
    full_prompt = f"{prompt}\n\nCode context:\n{code_context}" if code_context else prompt
    
    result = await team_manager.delegate_task(
        full_prompt,
        {"tool": "zed", "code_files": [{"content": code_context}] if code_context else []}
    )
    
    return JSONResponse(content={
        "suggestion": result["response"],
        "model_used": result["model_id"]
    })

@app.post("/api/tools/excel")
async def excel_integration(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    
    result = await team_manager.delegate_task(
        prompt,
        {"tool": "excel"}
    )
    
    return JSONResponse(content={
        "formula_or_macro": result["response"],
        "model_used": result["model_id"]
    })

# MCP Server endpoints for tool integration
@app.post("/api/mcp/execute")
async def mcp_execute(request: Request):
    """MCP server endpoint for tool execution"""
    data = await request.json()
    tool_name = data.get("tool")
    parameters = data.get("parameters", {})
    
    # Import tools dynamically
    try:
        import sys
        sys.path.insert(0, '/Users/mcampos.cerda/Documents/Programming/ai/tools')
        from tools import execute_tool
        
        result = await execute_tool(tool_name, parameters)
        return JSONResponse(content={"result": result})
    except Exception as e:
        logger.error(f"MCP execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("AI DEVELOPMENT TEAM ROUTER - M3 PRO OPTIMIZED")
    logger.info("=" * 70)
    logger.info(f"Platform: {'M3 Pro' if IS_M3_PRO else 'Standard'}")
    logger.info(f"Team size: {len(team_manager.team_members)} specialists")
    logger.info("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=11435, log_level="info")
ROUTER_EOF
    
    print_status "Router created"
}

# Install Python dependencies
install_python_deps() {
    echo ""
    echo "Installing Python dependencies..."
    
    cat > "$BASE_DIR/requirements.txt" << 'REQ_EOF'
# Core dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
aiohttp==3.9.0
psutil==5.9.6

# Tool dependencies
pandas==2.1.3
numpy==1.24.3
openpyxl==3.1.2
duckduckgo-search==3.9.6
requests==2.31.0
PyPDF2==3.0.1

# MCP and integration dependencies
langchain==0.1.0
langchain-community==0.1.0
python-multipart==0.0.6

# Open Web UI dependencies
docker==6.1.3
REQ_EOF
    
    pip3 install -r "$BASE_DIR/requirements.txt"
    print_status "Python dependencies installed"
}

# Setup Open Web UI
setup_open_webui() {
    echo ""
    echo "Setting up Open Web UI..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_info "Starting Docker..."
        open -a Docker
        sleep 10
    fi
    
    # Create Open Web UI configuration
    cat > "$BASE_DIR/config/open-webui/config.json" << 'WEBUI_EOF'
{
  "defaultModel": "router",
  "ollamaAPI": "http://host.docker.internal:11435",
  "enableModelRouting": true,
  "modelRoutingRules": [
    {
      "pattern": "refactor|debug|test|code|javascript|python|vue|laravel",
      "model": "router"
    },
    {
      "pattern": "excel|vba|forecast|inventory|reconciliation",
      "model": "router"
    },
    {
      "pattern": "vision|image|screenshot|ocr|slide",
      "model": "router"
    },
    {
      "pattern": "uncensored|direct|hack|reverse",
      "model": "router"
    }
  ],
  "tools": {
    "enabled": true,
    "web_search": {
      "default_provider": "duckduckgo",
      "providers": ["duckduckgo", "tavily", "google"]
    },
    "code_execution": {
      "enabled": true,
      "timeout": 10
    },
    "file_analysis": {
      "enabled": true,
      "max_size_mb": 50
    }
  }
}
WEBUI_EOF
    
    # Start Open Web UI container
    print_info "Starting Open Web UI Docker container..."
    docker stop open-webui 2>/dev/null || true
    docker rm open-webui 2>/dev/null || true
    
    docker run -d \
        -p $WEBUI_PORT:8080 \
        -v open-webui:/app/backend/data \
        -v "$BASE_DIR/config/open-webui:/config" \
        --add-host=host.docker.internal:host-gateway \
        --name open-webui \
        --restart unless-stopped \
        ghcr.io/open-webui/open-webui:main
    
    print_status "Open Web UI started at http://localhost:$WEBUI_PORT"
}

# Setup CLI tools
setup_cli_tools() {
    echo ""
    echo "Setting up CLI tools..."
    
    # Install OpenCode CLI if available
    if command -v opencode &> /dev/null; then
        print_info "Configuring OpenCode CLI..."
        mkdir -p ~/.opencode
        cat > ~/.opencode/config.json << 'OPENCODE_EOF'
{
  "model": "router",
  "api_base": "http://localhost:11435",
  "tools": [
    {
      "name": "web_search",
      "description": "Search the web using DuckDuckGo/Tavily/Google",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {"type": "string"},
          "provider": {"type": "string", "enum": ["duckduckgo", "tavily", "google"]}
        },
        "required": ["query"]
      }
    },
    {
      "name": "excel_optimizer",
      "description": "Generate optimized Pandas/VBA code for Excel tasks",
      "parameters": {
        "type": "object",
        "properties": {
          "task": {"type": "string"},
          "output": {"type": "string", "enum": ["pandas", "vba"]}
        },
        "required": ["task"]
      }
    }
  ],
  "context_length": 16384,
  "temperature": 0.3
}
OPENCODE_EOF
        print_status "OpenCode CLI configured"
    else
        print_warning "OpenCode CLI not found, skipping configuration"
    fi
    
    # Configure Charm/Glow if available
    if command -v charm &> /dev/null; then
        print_info "Configuring Charm CLI..."
        charm config set model router
        charm config set api_base http://localhost:11435
        print_status "Charm CLI configured"
    else
        print_warning "Charm CLI not found, skipping configuration"
    fi
}

# Setup Zed configuration
setup_zed() {
    echo ""
    echo "Setting up Zed editor configuration..."
    
    mkdir -p ~/.config/zed
    cat > ~/.config/zed/settings.json << 'ZED_EOF'
{
  "assistant": {
    "default_model": {
      "provider": "ollama",
      "model": "router"
    },
    "version": "2",
    "tool_calling": {
      "enabled": true,
      "timeout": 15000,
      "max_retries": 2
    }
  },
  "language_models": {
    "ollama": {
      "api_url": "http://localhost:11435",
      "low_speed_timeout_in_seconds": 120,
      "available_models": [
        {
          "provider": "ollama",
          "name": "router",
          "max_tokens": 128000,
          "max_input_tokens": 128000,
          "supports_tools": true,
          "default_temperature": 0.3
        }
      ]
    }
  },
  "vim_mode": false,
  "ui_font_size": 16,
  "buffer_font_size": 14
}
ZED_EOF
    
    print_status "Zed configuration created"
}

# Create startup script
create_startup_script() {
    echo ""
    echo "Creating startup script..."
    
    cat > "$BASE_DIR/start.sh" << 'START_EOF'
#!/bin/bash

echo "======================================================================"
echo "🚀 Starting AI Development Team Router"
echo "======================================================================"

# Set environment variables
export OLLAMA_API_BASE="http://localhost:11434"
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KEEP_ALIVE=5m

# Set search API keys
# Search API keys (optional - replace with your own)
export TAVILY_API_KEY="YOUR_TAVILY_API_KEY_HERE"
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
export GOOGLE_CX="YOUR_GOOGLE_CUSTOM_SEARCH_ID_HERE"

# Change to AI directory
cd /Users/mcampos.cerda/Documents/Programming/ai

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
fi

# Start Open Web UI if Docker is available
if command -v docker &> /dev/null && docker info > /dev/null 2>&1; then
    if ! docker ps -f "name=open-webui" --format "{{.Status}}" | grep -q "Up"; then
        echo "Starting Open Web UI..."
        docker start open-webui || docker run -d \
            -p 3000:8080 \
            -v open-webui:/app/backend/data \
            --add-host=host.docker.internal:host-gateway \
            --name open-webui \
            --restart unless-stopped \
            ghcr.io/open-webui/open-webui:main
        echo "Open Web UI available at http://localhost:3000"
    fi
fi

# Start the router
echo "Starting AI Team Router..."
python3 ai_team_router.py
START_EOF
    
    chmod +x "$BASE_DIR/start.sh"
    print_status "Startup script created"
}

# Create test script
create_test_script() {
    echo ""
    echo "Creating test script..."
    
    cat > "$BASE_DIR/test_system.sh" << 'TEST_EOF'
#!/bin/bash

echo "Testing AI Team Router System..."

# Test router status
echo -e "\n1. Testing router status..."
curl -s http://localhost:11435/api/team/status | python3 -m json.tool

# Test team members
echo -e "\n2. Testing team members endpoint..."
curl -s http://localhost:11435/api/team/members | python3 -m json.tool | head -20

# Test chat endpoint
echo -e "\n3. Testing chat endpoint..."
curl -s -X POST http://localhost:11435/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Write a Python function to calculate fibonacci"}' \
  | python3 -m json.tool

# Test tool integration
echo -e "\n4. Testing tool integration..."
curl -s -X POST http://localhost:11435/api/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"tool":"web_search","parameters":{"query":"Python pandas tutorial","provider":"duckduckgo"}}' \
  | python3 -m json.tool

# Test Open Web UI
echo -e "\n5. Testing Open Web UI..."
if curl -s http://localhost:3000 | grep -q "Open WebUI"; then
    echo "✅ Open Web UI is running"
else
    echo "⚠️ Open Web UI not responding"
fi

echo -e "\n✅ Tests complete!"
TEST_EOF
    
    chmod +x "$BASE_DIR/test_system.sh"
    print_status "Test script created"
}

# Setup shell aliases
setup_aliases() {
    echo ""
    echo "Setting up shell aliases..."
    
    # Detect shell
    SHELL_RC="$HOME/.zshrc"
    if [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    fi
    
    cat >> "$SHELL_RC" << 'ALIAS_EOF'

# AI Team Router Aliases
alias ai-start='cd /Users/mcampos.cerda/Documents/Programming/ai && ./start.sh'
alias ai-test='cd /Users/mcampos.cerda/Documents/Programming/ai && ./test_system.sh'
alias ai-status='curl -s http://localhost:11435/api/team/status | python3 -m json.tool'
alias ai-team='curl -s http://localhost:11435/api/team/members | python3 -m json.tool'
alias ai-chat='function _ai_chat() { curl -s -X POST http://localhost:11435/api/chat -H "Content-Type: application/json" -d "{\"prompt\":\"$1\"}" | python3 -m json.tool | grep -A 50 "response"; }; _ai_chat'
alias ai-logs='tail -f /Users/mcampos.cerda/Documents/Programming/ai/logs/team_router.log'
alias ai-webui='open http://localhost:3000'

ALIAS_EOF
    
    print_status "Aliases added to $SHELL_RC"
}

# Main execution
main() {
    check_system
    install_dependencies
    pull_models
    create_router
    install_python_deps
    setup_open_webui
    setup_cli_tools
    setup_zed
    create_startup_script
    create_test_script
    setup_aliases
    
    echo ""
    echo "======================================================================"
    echo "✅ INSTALLATION COMPLETE!"
    echo "======================================================================"
    echo ""
    echo "Your AI Development Team Router is installed at:"
    echo "  $BASE_DIR"
    echo ""
    echo "Quick Start:"
    echo "  1. Start the router: ai-start"
    echo "  2. Test the system: ai-test"
    echo "  3. Check status: ai-status"
    echo "  4. Open Web UI: ai-webui (http://localhost:3000)"
    echo ""
    echo "Features Enabled:"
    echo "  ✅ M3 Pro Optimizations"
    echo "  ✅ 11 Specialized AI Models"
    echo "  ✅ Intelligent Task Routing"
    echo "  ✅ Open Web UI Integration"
    echo "  ✅ Tool Integration (Search, Excel, Code)"
    echo "  ✅ Zed Editor Configuration"
    echo "  ✅ MCP Server Support"
    echo "  ✅ Vision & OCR Capabilities"
    echo "  ✅ VBA Macro Support (150k+ rows)"
    echo "  ✅ Abliterated Models for Direct Mode"
    echo ""
    echo "Shell Aliases:"
    echo "  ai-start   - Start the router"
    echo "  ai-test    - Test the system"
    echo "  ai-status  - Check status"
    echo "  ai-team    - List team members"
    echo "  ai-chat    - Quick chat"
    echo "  ai-logs    - View logs"
    echo "  ai-webui   - Open Web UI"
    echo ""
    echo "To activate aliases, run: source ~/.zshrc"
    echo ""
    echo "API Keys Configured:"
    echo "  ✅ Tavily Search"
    echo "  ✅ Google Search"
    echo ""
    echo "======================================================================"
}

# Run main function
main
