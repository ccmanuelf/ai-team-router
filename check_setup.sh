#!/bin/bash

echo "======================================================================"
echo "🚀 COMPLETE AI TEAM SETUP"
echo "======================================================================"
echo ""

# 1. Check Router
echo "1️⃣ Checking AI Team Router..."
if [ -f "/Users/mcampos.cerda/Documents/Programming/ai/ai_team_router.py" ]; then
    echo "   ✅ Router file exists"
    python3 -c "from ai_team_router import AITeamRouter; print('   ✅ Router imports successfully')" 2>/dev/null || echo "   ❌ Router has errors"
else
    echo "   ❌ Router file missing"
fi

# 2. Charm Crush CLI
echo ""
echo "2️⃣ Checking Charm Crush CLI..."
if command -v crush &> /dev/null; then
    echo "   ✅ Crush CLI installed ($(crush --version))"
    echo "   Usage: crush router.log  # View logs with style"
else
    echo "   ❌ Crush CLI not installed"
    echo "   Install: brew install charmbracelet/tap/crush"
fi

# 3. MCP Configuration
echo ""
echo "3️⃣ MCP (Model Context Protocol) Setup..."
if [ -f "/Users/mcampos.cerda/Documents/Programming/ai/mcp_server.py" ]; then
    echo "   ✅ MCP server created"
    echo "   📁 Config: configs/mcp_config.json"
    echo "   To use with Claude Desktop:"
    echo "      1. Copy configs/mcp_config.json to ~/Library/Application Support/Claude/"
    echo "      2. Restart Claude Desktop"
else
    echo "   ❌ MCP server missing"
fi

# 4. Zed Configuration
echo ""
echo "4️⃣ Zed.dev Configuration..."
if [ -f "/Users/mcampos.cerda/Documents/Programming/ai-team-router/configs/zed_settings.json" ]; then
    echo "   ✅ Zed config created"
    echo "   To apply:"
    echo "      cp configs/zed_settings.json ~/.config/zed/settings.json"
    echo "      Restart Zed"
else
    echo "   ❌ Zed config missing"
fi

# 5. Open WebUI
echo ""
echo "5️⃣ Open WebUI Status..."
if docker ps 2>/dev/null | grep -q open-webui; then
    echo "   ✅ Open WebUI is running"
    echo "   🌐 Access at: http://localhost:3000"
else
    echo "   ⚠️  Open WebUI not running"
    echo "   To start: ./setup_open_webui.sh"
fi

# 6. Test Everything
echo ""
echo "======================================================================"
echo "📊 SYSTEM STATUS"
echo "======================================================================"

python3 << 'PYTHON'
import sys
sys.path.insert(0, '/Users/mcampos.cerda/Documents/Programming/ai')

try:
    from ai_team_router import AITeamRouter
    router = AITeamRouter()
    status = router.get_status()
    
    print(f"✅ AI Team Router: OPERATIONAL")
    print(f"   Models: {len(router.team_members)}")
    print(f"   Memory: {status['system']['available_memory_gb']:.1f}GB available")
    print(f"   Platform: {status['system']['platform']}")
except Exception as e:
    print(f"❌ Router Error: {e}")

print("")
print("To start using:")
print("1. Start router: python3 ai_team_router.py")
print("2. Access Open WebUI: http://localhost:3000")
print("3. View logs: crush logs/router.log")
print("4. Use in Zed: Open Zed and use AI assistant")
PYTHON

echo ""
echo "======================================================================"
echo "📚 DOCUMENTATION"
echo "======================================================================"
echo ""
echo "Repository: https://github.com/ccmanuelf/ai-team-router"
echo ""
echo "Components:"
echo "  • AI Team Router: 11 models with intelligent routing"
echo "  • Charm Crush CLI: Beautiful log viewing"
echo "  • MCP Server: Integration with Claude Desktop"
echo "  • Open WebUI: Web interface for all models"
echo "  • Zed Integration: AI assistance in editor"
echo ""
echo "======================================================================"
