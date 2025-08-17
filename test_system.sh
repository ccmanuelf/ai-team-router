#!/bin/bash

echo "Testing Enhanced AI Team Router..."

# Test router health
echo "1. Router Health:"
curl -s http://localhost:11435/health || echo "Router not responding"

# Test team status
echo -e "\n2. Team Status:"
curl -s http://localhost:11435/api/team/status | python3 -m json.tool 2>/dev/null || echo "Status endpoint not available"

# Test chat
echo -e "\n3. Chat Test:"
curl -s -X POST http://localhost:11435/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello, write a simple Python function"}' | \
  python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('response','No response')[:200])" 2>/dev/null || echo "Chat test failed"

# Test Open Web UI
echo -e "\n4. Open Web UI:"
if curl -s http://localhost:3000 | grep -q "Open WebUI"; then
    echo "✅ Open Web UI running"
else
    echo "⚠️ Open Web UI not accessible"
fi

echo -e "\n✅ Tests complete!"
TEST_EOF
    
    chmod +x "$BASE_DIR/test_system.sh"
    print_status "Startup and test scripts created"
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

# Run main function
main
