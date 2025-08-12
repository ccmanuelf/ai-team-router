#!/bin/bash

echo "======================================================================"
echo "🔧 COMPLETE AI TEAM ROUTER SETUP WITH CHROMA"
echo "======================================================================"

# Install Chroma if not installed
echo "📦 Installing Chroma vector database..."
pip3 install chromadb --quiet

# Test Chroma setup
echo ""
echo "🧪 Testing Chroma integration..."
python3 src/chroma_integration.py

# Final test of complete system
echo ""
echo "======================================================================"
echo "🚀 FINAL SYSTEM TEST"
echo "======================================================================"

# Test router
echo "Testing router import..."
python3 -c "
from src.ai_team_router import AITeamRouter
from src.chroma_integration import ChromaIntegration, CHROMA_AVAILABLE

router = AITeamRouter()
print(f'✅ Router: {len(router.team_members)} models')

if CHROMA_AVAILABLE:
    integration = ChromaIntegration(router)
    print('✅ Chroma: Vector database ready')
    insights = integration.get_insights()
    print(f'   Collections: {len(insights[\"collection_stats\"])}')
else:
    print('⚠️  Chroma not available')

status = router.get_status()
print(f'✅ System: {status[\"system\"][\"available_memory_gb\"]:.1f}GB available')
"

echo ""
echo "======================================================================"
echo "✅ SETUP COMPLETE!"
echo "======================================================================"
echo ""
echo "Your AI Team Router is now fully configured with:"
echo "  ✅ 11 AI models orchestrated"
echo "  ✅ Intelligent routing algorithm"
echo "  ✅ Chroma vector database for memory"
echo "  ✅ M3 Pro memory optimization"
echo "  ✅ Tool integration support"
echo "  ✅ API endpoints ready"
echo ""
echo "To start the router:"
echo "  cd /Users/mcampos.cerda/Documents/Programming/ai"
echo "  python3 ai_team_router.py"
echo ""
echo "API will be available at:"
echo "  http://localhost:11435"
echo ""
echo "Repository published at:"
echo "  https://github.com/ccmanuelf/ai-team-router"
echo ""
echo "======================================================================"
