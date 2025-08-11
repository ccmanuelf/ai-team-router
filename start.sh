#!/bin/bash

echo "Starting AI Team Router (Minimal Mode - No Docker/Web UI)..."

# Set environment variables
export OLLAMA_API_BASE="http://localhost:11434"
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KEEP_ALIVE=5m

# Search API keys
# Search API keys (optional - replace with your own)
export TAVILY_API_KEY="YOUR_TAVILY_API_KEY_HERE"
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
export GOOGLE_CX="YOUR_GOOGLE_CUSTOM_SEARCH_ID_HERE"

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    sleep 5
fi

cd /Users/mcampos.cerda/Documents/Programming/ai

echo "Starting AI Team Router on port 11435..."
echo "Access at: http://localhost:11435"
echo ""
echo "API Endpoints:"
echo "  • Chat: POST http://localhost:11435/api/chat"
echo "  • Status: GET http://localhost:11435/api/team/status"
echo "  • Members: GET http://localhost:11435/api/team/members"
echo ""
echo "Press Ctrl+C to stop"

python3 ai_team_router.py
