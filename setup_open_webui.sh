#!/bin/bash

echo "======================================================================"
echo "🌐 OPEN WEBUI SETUP"
echo "======================================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed!"
    echo "Please install Docker Desktop from:"
    echo "https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop"
    exit 1
fi

echo "✅ Docker is ready"

# Stop existing Open WebUI if running
echo "Stopping existing Open WebUI if running..."
docker stop open-webui 2>/dev/null
docker rm open-webui 2>/dev/null

# Run Open WebUI
echo ""
echo "Starting Open WebUI..."
docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main

# Wait for container to be ready
echo "Waiting for Open WebUI to start..."
sleep 10

# Check if running
if docker ps | grep -q open-webui; then
    echo ""
    echo "======================================================================"
    echo "✅ OPEN WEBUI IS RUNNING!"
    echo "======================================================================"
    echo ""
    echo "Access Open WebUI at: http://localhost:3000"
    echo ""
    echo "First-time setup:"
    echo "1. Open http://localhost:3000"
    echo "2. Create an admin account"
    echo "3. Go to Settings > Connections"
    echo "4. Set Ollama URL to: http://host.docker.internal:11434"
    echo ""
    echo "Your models will automatically appear!"
    echo ""
    echo "To use with AI Team Router:"
    echo "1. Start the router: python3 /Users/mcampos.cerda/Documents/Programming/ai/ai_team_router.py"
    echo "2. The router will manage model selection"
    echo ""
else
    echo "❌ Failed to start Open WebUI"
    echo "Check Docker logs: docker logs open-webui"
fi

# Save configuration
cat > /Users/mcampos.cerda/Documents/Programming/ai/open-webui-config.json << 'EOF'
{
  "name": "Open WebUI Configuration",
  "url": "http://localhost:3000",
  "ollama_url": "http://host.docker.internal:11434",
  "models": [
    "deepcoder:latest",
    "qwen2.5:14b",
    "deepseek-coder-v2:16b",
    "granite3.3:8b",
    "granite3.2-vision:2b",
    "mistral:latest",
    "gemma3:4b",
    "granite3.1-moe:3b",
    "gemma3:1b",
    "huihui_ai/deepseek-r1-abliterated:latest",
    "huihui_ai/dolphin3-abliterated:latest"
  ],
  "notes": "Access at http://localhost:3000 after Docker container starts"
}
EOF

echo "Configuration saved to: open-webui-config.json"
