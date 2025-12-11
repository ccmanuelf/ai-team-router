#!/bin/bash

# AI Team Router - Git Configuration Backup & Recovery System
# Prevents authentication issues by maintaining proper Git configuration

echo "🔧 Git Configuration Backup & Recovery System"
echo "============================================"

# Configuration file paths
CONFIG_DIR="$HOME/.git_config_backup"
CONFIG_FILE="$CONFIG_DIR/git_config_$(date +%Y%m%d_%H%M%S).bak"

# Create backup directory
mkdir -p "$CONFIG_DIR"

# Backup current Git configuration
echo "📁 Backing up Git configuration..."
git config --global --list > "$CONFIG_FILE"

# Also backup local repository configuration
echo "📁 Backing up local repository config..."
cp .git/config "$CONFIG_DIR/git_local_config_$(date +%Y%m%d_%H%M%S).bak" 2>/dev/null

echo "✅ Backup created: $CONFIG_FILE"

# Check for authentication issues
echo "🔍 Checking for authentication issues..."

# Check if remote URL has empty credentials
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [[ "$REMOTE_URL" == *"https://:@github.com"* ]]; then
    echo "⚠️  Found empty credentials in remote URL!"
    echo "🔧 Attempting automatic repair..."
    
    # Try to fix using environment variable
    if [ -n "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
        echo "🔑 Using GITHUB_PERSONAL_ACCESS_TOKEN from environment"
        git remote set-url origin "https://$GITHUB_PERSONAL_ACCESS_TOKEN@github.com/ccmanuelf/ai-team-router.git"
        echo "✅ Remote URL repaired"
    else
        echo "❌ No GitHub token found in environment"
        echo "📝 Please set GITHUB_PERSONAL_ACCESS_TOKEN environment variable"
    fi
fi

# Verify GitHub token availability
echo "🔑 Checking GitHub token availability..."
if [ -n "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    echo "✅ GitHub token available: ${GITHUB_PERSONAL_ACCESS_TOKEN:0:8}..."
else
    echo "⚠️  No GitHub token found in environment"
    echo "📝 Run: export GITHUB_PERSONAL_ACCESS_TOKEN='your_token_here'"
fi

echo "🎉 Backup and verification complete!"
echo "📁 Backups stored in: $CONFIG_DIR"