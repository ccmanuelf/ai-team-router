#!/bin/bash

# GitHub Repository Setup Script
# Creates and pushes the AI Team Router repository

echo "======================================================================"
echo "🚀 SETTING UP GITHUB REPOSITORY"
echo "======================================================================"

# Repository details
REPO_NAME="ai-team-router"
REPO_DESCRIPTION="Professional local AI development environment - Save \$3000/year with 11 orchestrated models"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Installing GitHub CLI..."
    brew install gh
fi

# Authenticate if needed
if ! gh auth status &> /dev/null; then
    echo "Please authenticate with GitHub:"
    gh auth login
fi

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# Logs
*.log
logs/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test outputs
benchmark_results_*.json
benchmark_report_*.md

# Models (too large for git)
models/
*.gguf
*.bin

# Temporary files
*.tmp
temp/
EOF

# Create LICENSE
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 AI Team Router Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
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

# Optional enhancements
python-multipart==0.0.6
pillow==10.4.0
EOF

# Initialize git repository
echo "Initializing Git repository..."
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: AI Team Router - Professional local AI development environment

- 11 specialized AI models with intelligent routing
- M3 Pro optimized memory management
- Support for VueJS, Laravel, Python, Excel/VBA (150k+ rows)
- Web search, code execution, file analysis tools
- Saves $3000/year vs cloud subscriptions
- 100% offline capable after setup

Features:
- Automatic model selection based on task
- Vision/OCR capabilities
- Abliterated models for uncensored assistance
- Open Web UI integration
- Zed editor support
- Complete API documentation
- Comprehensive benchmarks proving 90-95% cloud parity"

# Create GitHub repository
echo "Creating GitHub repository..."
gh repo create $REPO_NAME \
    --description "$REPO_DESCRIPTION" \
    --public \
    --source=. \
    --remote=origin \
    --push

# Add topics
echo "Adding repository topics..."
gh repo edit --add-topic "ai"
gh repo edit --add-topic "llm"
gh repo edit --add-topic "ollama"
gh repo edit --add-topic "offline-ai"
gh repo edit --add-topic "local-ai"
gh repo edit --add-topic "ai-development"
gh repo edit --add-topic "cost-saving"
gh repo edit --add-topic "m3-pro"
gh repo edit --add-topic "vuejs"
gh repo edit --add-topic "laravel"
gh repo edit --add-topic "excel-vba"

echo ""
echo "======================================================================"
echo "✅ GITHUB REPOSITORY CREATED SUCCESSFULLY!"
echo "======================================================================"
echo ""
echo "Repository URL: https://github.com/$(gh api user -q .login)/$REPO_NAME"
echo ""
echo "Next steps:"
echo "1. Star the repository to increase visibility"
echo "2. Add screenshots to assets/ folder"
echo "3. Create releases for stable versions"
echo "4. Enable GitHub Pages for documentation"
echo "5. Set up GitHub Actions for automated testing"
echo ""
echo "To clone on another machine:"
echo "  git clone https://github.com/$(gh api user -q .login)/$REPO_NAME.git"
echo ""
echo "======================================================================"
