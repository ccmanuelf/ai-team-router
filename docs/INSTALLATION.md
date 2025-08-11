# 📦 Installation Guide

## Prerequisites

Before starting, ensure you have:

- ✅ macOS (Intel or Apple Silicon)
- ✅ 16GB+ RAM (18GB recommended)
- ✅ 50GB free disk space
- ✅ Admin access to install software

## Quick Install (5 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-team-router.git
cd ai-team-router

# Run the automated setup
chmod +x setup.sh
./setup.sh

# Start the AI team
./start.sh
```

## Detailed Installation Steps

### Step 1: System Verification

```bash
# Check your system specs
system_profiler SPHardwareDataType | grep -E "Chip|Memory"

# Expected output for M3 Pro:
# Chip: Apple M3 Pro
# Memory: 18 GB
```

### Step 2: Install Dependencies

#### Option A: Automated (Recommended)
```bash
./setup.sh
```

This will install:
- Homebrew (if not present)
- Ollama
- Python 3.11+
- Node.js
- Required Python packages

#### Option B: Manual Installation

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Ollama
brew install ollama

# Install Python
brew install python@3.11

# Install Node.js
brew install node

# Install Python dependencies
pip3 install fastapi uvicorn aiohttp psutil pandas numpy openpyxl duckduckgo-search requests PyPDF2
```

### Step 3: Download AI Models

The setup script will automatically download all models. To do it manually:

```bash
# Start Ollama service
ollama serve &

# Pull models (this takes 30-60 minutes)
ollama pull deepcoder:latest              # 9GB
ollama pull deepseek-coder-v2:16b        # 8.9GB
ollama pull qwen2.5:14b                  # 9GB
ollama pull granite3.3:8b                # 4.9GB
ollama pull granite3.2-vision:2b         # 2.4GB
ollama pull gemma3:4b                    # 3.3GB
ollama pull mistral:latest               # 4.4GB
ollama pull granite3.1-moe:3b            # 2GB
ollama pull gemma3:1b                    # 0.8GB
ollama pull huihui_ai/deepseek-r1-abliterated:latest  # 5GB
ollama pull huihui_ai/dolphin3-abliterated:latest     # 4.9GB
```

### Step 4: Configure Environment

```bash
# Add to ~/.zshrc or ~/.bashrc
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KEEP_ALIVE=5m

# Search API keys (optional)
export TAVILY_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"
export GOOGLE_CX="your-cx-here"

# Reload shell
source ~/.zshrc
```

### Step 5: Verify Installation

```bash
# Check Ollama
ollama list

# Expected output:
NAME                                        SIZE    
deepcoder:latest                          9.0 GB
deepseek-coder-v2:16b                     8.9 GB
qwen2.5:14b                               9.0 GB
# ... (all 11 models)

# Test Python dependencies
python3 -c "import fastapi, aiohttp, pandas; print('✅ Dependencies OK')"

# Test the router
./start.sh
```

## Configuration Options

### Memory Settings

Edit `src/ai_team_router.py` to adjust memory settings:

```python
# For 16GB systems
MEMORY_OVERHEAD_GB = 5.0  # Increase overhead
MEMORY_SAFETY_BUFFER_GB = 7.0  # Increase buffer

# For 32GB+ systems
MEMORY_OVERHEAD_GB = 3.0  # Decrease overhead
MEMORY_SAFETY_BUFFER_GB = 4.0  # Decrease buffer
```

### Port Configuration

Default ports can be changed:

```python
# In ai_team_router.py
uvicorn.run(app, host="0.0.0.0", port=11435)  # Change 11435 to your port
```

### Model Selection

Customize which models to use in `src/ai_team_router.py`:

```python
def _initialize_team(self):
    # Comment out models you don't need
    team = {
        "deepcoder_primary": TeamMember(...),  # Keep for coding
        # "deepseek_legacy": TeamMember(...),  # Comment if not using PHP
        "qwen_analyst": TeamMember(...),  # Keep for Excel
        # ... customize as needed
    }
```

## Platform-Specific Instructions

### macOS Intel

```bash
# No special configuration needed
# Memory management is automatic
```

### macOS Apple Silicon (M1/M2/M3)

```bash
# Optimizations are automatically detected
# Unified memory management is enabled
```

### Linux (Experimental)

```bash
# Install Ollama for Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Adjust memory detection in router
# Edit IS_M3_PRO detection logic
```

## Troubleshooting Installation

### Issue: "Ollama: command not found"

```bash
# Reinstall Ollama
brew reinstall ollama

# Or download directly
curl -L https://ollama.ai/download/Ollama-darwin.zip -o ollama.zip
unzip ollama.zip
sudo mv Ollama.app /Applications/
```

### Issue: "Port 11435 already in use"

```bash
# Find process using port
lsof -i :11435

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=11436 ./start.sh
```

### Issue: "Model failed to load: out of memory"

```bash
# Free up memory
# Close other applications
# Use smaller models initially

# Start with minimal models
ollama pull gemma3:1b  # Start small
ollama pull mistral:latest  # Add medium
```

### Issue: Python package conflicts

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Post-Installation Setup

### 1. Test Basic Functionality

```bash
# Start the router
./start.sh

# In another terminal, test API
curl http://localhost:11435/api/team/status

# Test chat
curl -X POST http://localhost:11435/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello, are you working?"}'
```

### 2. Configure Editor Integration

#### Zed Editor
```bash
# Config is auto-created at ~/.config/zed/settings.json
# Just restart Zed after installation
```

#### VS Code
```json
// Add to settings.json
{
  "github.copilot.enable": false,
  "ai-assistant.endpoint": "http://localhost:11435/api/chat"
}
```

### 3. Set Up Aliases

```bash
# Add to ~/.zshrc
alias ai='curl -X POST http://localhost:11435/api/chat -H "Content-Type: application/json" -d'
alias ai-status='curl http://localhost:11435/api/team/status | jq'

# Reload
source ~/.zshrc
```

### 4. Optional: Docker Setup (for Web UI)

```bash
# Install Docker Desktop
brew install --cask docker

# Start Docker
open -a Docker

# Run Open Web UI
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main

# Access at http://localhost:3000
```

## Validation Checklist

After installation, verify:

- [ ] All 11 models downloaded
- [ ] Router starts without errors
- [ ] API responds to status check
- [ ] Chat endpoint works
- [ ] Memory usage is stable
- [ ] Models switch correctly
- [ ] Tools (search, Excel) work
- [ ] Editor integration works

## Updating

```bash
# Update models
ollama pull <model-name>

# Update repository
git pull origin main

# Update dependencies
pip3 install -U -r requirements.txt
```

## Uninstallation

```bash
# Remove models (frees ~45GB)
ollama rm deepcoder:latest
# ... repeat for all models

# Remove Ollama
brew uninstall ollama
rm -rf ~/.ollama

# Remove repository
rm -rf ai-team-router
```

## Next Steps

1. **Run benchmarks**: `python benchmarks/run_benchmarks.py`
2. **Read the API docs**: [API Reference](API.md)
3. **Customize models**: [Model Guide](MODELS.md)
4. **Join discussions**: [GitHub Discussions](https://github.com/yourusername/ai-team-router/discussions)

## Support

If you encounter issues:

1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search [existing issues](https://github.com/yourusername/ai-team-router/issues)
3. Create a new issue with:
   - System specs
   - Error messages
   - Steps to reproduce

---

*Installation typically takes 30-60 minutes depending on internet speed*
*Models require ~45GB disk space*
*System requires 16GB+ RAM for optimal performance*
