#!/bin/bash
# Phase 4B Deployment Script
# ==========================

echo "🚀 AI Team Router - Phase 4B Deployment"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "src/ai_team_router_phase4b.py" ]; then
    echo "❌ Error: ai_team_router_phase4b.py not found"
    echo "   Please run this script from the ai-team-router directory"
    exit 1
fi

echo "📁 Current directory: $(pwd)"
echo "✅ Phase 4B router file found"

# Check if Ollama is running
echo ""
echo "🔍 Checking Ollama service..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama is running on port 11434"
else
    echo "❌ Ollama is not running"
    echo "   Please start Ollama first:"
    echo "   ollama serve"
    exit 1
fi

# Check Python dependencies
echo ""
echo "🔍 Checking Python dependencies..."
python3 -c "import requests, psutil, fastapi, uvicorn" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Required Python packages are installed"
else
    echo "❌ Missing Python dependencies"
    echo "   Installing required packages..."
    pip3 install requests psutil fastapi uvicorn
fi

echo ""
echo "🎯 Phase 4B Deployment Options:"
echo "1. Start Phase 4B Router"
echo "2. Run Integration Test"
echo "3. Health Check"
echo "4. Full Deployment (Start Router + Test)"
echo ""

read -p "Select option (1-4): " option

case $option in
    1)
        echo ""
        echo "🚀 Starting Phase 4B Router..."
        echo "Press Ctrl+C to stop the router"
        echo ""
        python3 src/ai_team_router_phase4b.py
        ;;
    2)
        echo ""
        echo "🧪 Running Phase 4B Integration Test..."
        echo "Make sure the Phase 4B router is running in another terminal"
        echo ""
        python3 test_phase4b_integration.py
        ;;
    3)
        echo ""
        echo "🩺 Performing Health Check..."
        echo "Checking router health..."
        
        # Check if router is running
        if curl -s http://localhost:11435/health >/dev/null 2>&1; then
            echo "✅ Router is running on port 11435"
            echo ""
            echo "Health Status:"
            curl -s http://localhost:11435/health | python3 -m json.tool
            echo ""
            echo "Router Status:"
            curl -s http://localhost:11435/api/team/status | python3 -m json.tool
        else
            echo "❌ Router is not running"
            echo "Start the router first with option 1"
        fi
        ;;
    4)
        echo ""
        echo "🚀 Full Phase 4B Deployment"
        echo "Starting router in background..."
        
        # Start router in background
        python3 src/ai_team_router_phase4b.py &
        ROUTER_PID=$!
        
        echo "Router PID: $ROUTER_PID"
        echo "Waiting for router to start..."
        sleep 10
        
        # Check if router started successfully
        if curl -s http://localhost:11435/health >/dev/null 2>&1; then
            echo "✅ Router started successfully"
            echo ""
            echo "🧪 Running integration test..."
            python3 test_phase4b_integration.py
            
            echo ""
            echo "🔍 Final health check..."
            curl -s http://localhost:11435/health | python3 -m json.tool
            
            echo ""
            echo "Press Enter to stop the router..."
            read
            
            echo "Stopping router..."
            kill $ROUTER_PID 2>/dev/null
            echo "✅ Router stopped"
        else
            echo "❌ Router failed to start"
            kill $ROUTER_PID 2>/dev/null
            exit 1
        fi
        ;;
    *)
        echo "Invalid option. Please select 1-4."
        exit 1
        ;;
esac

echo ""
echo "🎉 Phase 4B deployment completed!"
echo "📄 See PHASE4B_COMPLETION_REPORT.md for details"
