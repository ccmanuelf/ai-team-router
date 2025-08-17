#!/bin/bash

# AI Team Router - Enhanced Setup Script
# Consolidates legacy automation with enhanced router capabilities

set -e

BASE_DIR="/Users/mcampos.cerda/Documents/Programming/ai-team-router"
WEBUI_PORT=3000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "======================================================================"
echo "🚀 AI Team Router - Enhanced Setup"
echo "======================================================================"
echo "Setting up enhanced router with tool integration..."
echo ""

# Check system requirements
check_system() {
    echo "Checking system requirements..."
    
    # Check if M3 Pro
    if system_profiler SPHardwareDataType 2>/dev/null | grep -q "Apple M3 Pro"; then
        print_status "M3 Pro detected - optimizations enabled"
    else
        print_warning "Non-M3 system detected - using standard settings"
    fi
    
    # Check memory
    TOTAL_MEMORY=$(echo "$(sysctl -n hw.memsize) / 1024 / 1024 / 1024" | bc)
    if [ "$TOTAL_MEMORY" -ge 16 ]; then
        print_status "Memory: ${TOTAL_MEMORY}GB (sufficient)"
    else
        print_warning "Memory: ${TOTAL_MEMORY}GB (may be insufficient for all models)"
    fi
    
    # Check disk space
    DISK_FREE=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "${DISK_FREE%.*}" -ge 50 ]; then
        print_status "Disk space: ${DISK_FREE}G available"
    else
        print_warning "Disk space: ${DISK_FREE}G (may be insufficient)"
    fi
}

# Install dependencies
install_dependencies() {
    echo ""
    echo "Installing dependencies..."
    
    # Install Homebrew if not present
    if ! command -v brew &> /dev/null; then
        print_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install Python
    if ! command -v python3 &> /dev/null; then
        print_info "Installing Python..."
        brew install python
    fi
    
    # Install Node.js for MCP tools
    if ! command -v node &> /dev/null; then
        print_info "Installing Node.js..."
        brew install node
    fi
    
    # Install Docker
    if ! command -v docker &> /dev/null; then
        print_info "Installing Docker..."
        brew install --cask docker
        print_warning "Please start Docker Desktop manually"
    fi
    
    # Install Ollama
    if ! command -v ollama &> /dev/null; then
        print_info "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
    
    print_status "Dependencies installed"
}

# Install Python dependencies
install_python_deps() {
    echo ""
    echo "Installing Python dependencies..."
    
    cd "$BASE_DIR"
    
    # Install dependencies
    pip3 install -r requirements.txt
    print_status "Python dependencies installed"
}

# Pull AI models
pull_models() {
    echo ""
    echo "Pulling AI models..."
    print_info "This may take 30-60 minutes depending on internet speed"
    
    # Start Ollama service
    if ! pgrep -x "ollama" > /dev/null; then
        print_info "Starting Ollama service..."
        ollama serve &
        sleep 5
    fi
    
    # Core models
    MODELS=(
        "deepseek-coder-v2:16b"
        "qwen2.5:14b"
        "mistral:latest"
        "gemma3:4b"
        "gemma3:1b"
        "granite3.3:8b"
        "granite3.2-vision:2b"
        "granite3.1-moe:3b"
    )
    
    # Try to pull deepcoder (may not be available)
    ollama pull deepcoder:latest 2>/dev/null || print_warning "deepcoder:latest not available, using alternatives"
    
    for model in "${MODELS[@]}"; do
        print_info "Pulling $model..."
        ollama pull "$model"
    done
    
    # Optional abliterated models
    print_info "Attempting to pull abliterated models (optional)..."
    ollama pull huihui_ai/deepseek-r1-abliterated:latest 2>/dev/null || print_warning "Abliterated models unavailable"
    ollama pull huihui_ai/dolphin3-abliterated:latest 2>/dev/null || print_warning "Abliterated models unavailable"
    
    print_status "Models pulled successfully"
}

# Setup MCP configuration
setup_mcp() {
    echo ""
    echo "Setting up MCP configuration..."
    
    mkdir -p "$BASE_DIR/configs"
    cat > "$BASE_DIR/configs/mcp_config.json" << 'MCP_EOF'
{
  "mcpServers": {
    "ai-team-router": {
      "command": "python3",
      "args": ["/Users/mcampos.cerda/Documents/Programming/ai-team-router/src/mcp_server.py"],
      "env": {
        "OLLAMA_API_BASE": "http://localhost:11434"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/mcampos.cerda/Documents",
        "/Users/mcampos.cerda/Desktop",
        "/Users/mcampos.cerda/Downloads"
      ]
    }
  }
}
MCP_EOF
    
    print_status "MCP configuration created"
}

# Setup Open WebUI
setup_open_webui() {
    echo ""
    echo "Setting up Open WebUI..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_warning "Docker not running. Please start Docker Desktop manually"
        return
    fi
    
    # Stop existing container
    docker stop open-webui 2>/dev/null || true
    docker rm open-webui 2>/dev/null || true
    
    # Start Open WebUI
    print_info "Starting Open WebUI container..."
    docker run -d \
        -p $WEBUI_PORT:8080 \
        -v open-webui:/app/backend/data \
        --add-host=host.docker.internal:host-gateway \
        --name open-webui \
        --restart unless-stopped \
        ghcr.io/open-webui/open-webui:main
    
    print_status "Open WebUI started at http://localhost:$WEBUI_PORT"
}

# Setup Zed configuration
setup_zed() {
    echo ""
    echo "Setting up Zed configuration..."
    
    mkdir -p ~/.config/zed
    cat > ~/.config/zed/settings.json << 'ZED_EOF'
{
  "assistant": {
    "default_model": {
      "provider": "ollama",
      "model": "router"
    },
    "version": "2"
  },
  "language_models": {
    "ollama": {
      "api_url": "http://localhost:11435",
      "available_models": [
        {
          "provider": "ollama",
          "name": "router",
          "max_tokens": 128000
        }
      ]
    }
  }
}
ZED_EOF
    
    print_status "Zed configuration created"
}

# Create startup script
create_startup_script() {
    echo ""
    echo "Creating startup scripts..."
    
    cat > "$BASE_DIR/start.sh" << 'START_EOF'
#!/bin/bash

echo "🚀 Starting Enhanced AI Team Router..."

# Set environment variables
export OLLAMA_API_BASE="http://localhost:11434"
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_LOADED_MODELS=1

cd /Users/mcampos.cerda/Documents/Programming/ai-team-router

# Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Start Open Web UI if Docker available
if command -v docker &> /dev/null && docker info > /dev/null 2>&1; then
    if ! docker ps -f "name=open-webui" --format "{{.Status}}" | grep -q "Up"; then
        echo "Starting Open Web UI..."
        docker start open-webui 2>/dev/null || {
            docker run -d \
                -p 3000:8080 \
                -v open-webui:/app/backend/data \
                --add-host=host.docker.internal:host-gateway \
                --name open-webui \
                --restart unless-stopped \
                ghcr.io/open-webui/open-webui:main
        }
        echo "Open Web UI: http://localhost:3000"
    fi
fi

# Start the enhanced router
echo "Starting Enhanced AI Team Router..."
python3 src/ai_team_router.py
START_EOF
    
    chmod +x "$BASE_DIR/start.sh"
    print_status "Startup script created"
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
    
    # Check if aliases already exist
    if ! grep -q "AI Team Router Aliases" "$SHELL_RC" 2>/dev/null; then
        cat >> "$SHELL_RC" << 'ALIAS_EOF'

# AI Team Router Aliases
alias ai-start='cd /Users/mcampos.cerda/Documents/Programming/ai-team-router && ./start.sh'
alias ai-test='cd /Users/mcampos.cerda/Documents/Programming/ai-team-router && ./test_system.sh'
alias ai-status='curl -s http://localhost:11435/api/team/status | python3 -m json.tool'
alias ai-team='curl -s http://localhost:11435/api/team/members | python3 -m json.tool'
alias ai-chat='function _ai_chat() { curl -s -X POST http://localhost:11435/api/chat -H "Content-Type: application/json" -d "{\"prompt\":\"$1\"}" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get(\"response\",\"No response\"))"; }; _ai_chat'
alias ai-logs='tail -f /Users/mcampos.cerda/Documents/Programming/ai-team-router/logs/router.log'
alias ai-webui='open http://localhost:3000'
alias ai-phase4a='cd /Users/mcampos.cerda/Documents/Programming/ai-team-router && python3 run_phase4a.py'

ALIAS_EOF
        print_status "Aliases added to $SHELL_RC"
    else
        print_info "Aliases already exist in $SHELL_RC"
    fi
}

# Main execution
main() {
    check_system
    install_dependencies
    install_python_deps
    pull_models
    setup_mcp
    setup_open_webui
    setup_zed
    create_startup_script
    setup_aliases
    
    echo ""
    echo "======================================================================"
    echo "✅ ENHANCED AI TEAM ROUTER SETUP COMPLETE!"
    echo "======================================================================"
    echo ""
    echo "🎯 Quick Start:"
    echo "  1. Start router: ai-start"
    echo "  2. Test system: ai-test"
    echo "  3. Check status: ai-status"
    echo "  4. Open Web UI: ai-webui"
    echo "  5. Run Phase 4A: ai-phase4a"
    echo ""
    echo "🔧 Features Enabled:"
    echo "  ✅ Enhanced Router (0.5GB overhead, 10s timeout)"
    echo "  ✅ Intelligent Model Selection"
    echo "  ✅ MCP Server Integration"
    echo "  ✅ Open Web UI (http://localhost:3000)"
    echo "  ✅ Zed Editor Configuration"
    echo "  ✅ Shell Aliases & CLI Tools"
    echo "  ✅ Phase 4A Testing Ready"
    echo ""
    echo "📊 Available Models:"
    echo "  • DeepCoder (9GB) - VueJS/React expert"
    echo "  • Qwen Analyst (9GB) - Excel/VBA specialist" 
    echo "  • DeepSeek Legacy (8.9GB) - Laravel/338 languages"
    echo "  • Granite Enterprise (4.9GB) - Enterprise reports"
    echo "  • Granite Vision (2.4GB) - OCR/Screenshots"
    echo "  • Mistral (4.4GB) - Documentation"
    echo "  • Gemma Medium (3.3GB) - General coding"
    echo "  • Granite MoE (2GB) - Quick tasks"
    echo "  • Gemma Tiny (0.8GB) - Always available"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Restart terminal or run: source ~/.zshrc"
    echo "  2. Start system: ai-start"
    echo "  3. Ready for Phase 4A testing!"
    echo ""
    echo "======================================================================"
}

# Run main function if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi
