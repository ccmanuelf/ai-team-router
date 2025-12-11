#!/bin/bash

# AI Team Router - GitHub Token Validation Script
# Validates GitHub personal access token and repository access

echo "🔑 GitHub Token Validation"
echo "=========================="

# Check if token is available
if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    echo "❌ No GitHub token found in environment"
    echo "📝 Set GITHUB_PERSONAL_ACCESS_TOKEN environment variable"
    echo "Example: export GITHUB_PERSONAL_ACCESS_TOKEN='ghp_...'"
    exit 1
fi

echo "✅ GitHub token found: ${GITHUB_PERSONAL_ACCESS_TOKEN:0:8}..."

# Test token validity by making a simple API call
echo "🔍 Testing token validity..."

# Create a temporary test file
TEMP_FILE=$(mktemp)
echo "Test content" > "$TEMP_FILE"

# Test API access (using curl with token)
API_RESPONSE=$(curl -s -o "$TEMP_FILE" -w "%{http_code}" \
    -H "Authorization: token $GITHUB_PERSONAL_ACCESS_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/user")

# Check response
if [ "$API_RESPONSE" = "200" ]; then
    echo "✅ Token is valid and has API access"
    
    # Parse user info
    USER_INFO=$(cat "$TEMP_FILE" | grep -o '"login": "[^"]*"' | cut -d'"' -f4)
    echo "👤 Authenticated as: $USER_INFO"
    
    # Test repository access
    echo "🔍 Testing repository access..."
    REPO_RESPONSE=$(curl -s -o "$TEMP_FILE" -w "%{http_code}" \
        -H "Authorization: token $GITHUB_PERSONAL_ACCESS_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/ccmanuelf/ai-team-router")
    
    if [ "$REPO_RESPONSE" = "200" ]; then
        echo "✅ Repository access confirmed"
        
        # Check write permissions
        PERMISSIONS=$(cat "$TEMP_FILE" | grep -o '"permissions": {"[^"]*"}' | grep -o '"push": [^,]*')
        if [[ "$PERMISSIONS" == *"true"* ]]; then
            echo "✅ Write permissions confirmed"
        else
            echo "⚠️  Token may not have write permissions"
        fi
    else
        echo "❌ Cannot access repository (HTTP $REPO_RESPONSE)"
    fi
else
    echo "❌ Token validation failed (HTTP $API_RESPONSE)"
    if [ "$API_RESPONSE" = "401" ]; then
        echo "💡 Token may be invalid or expired"
    elif [ "$API_RESPONSE" = "403" ]; then
        echo "💡 Token may not have required permissions"
    fi
fi

# Clean up
rm -f "$TEMP_FILE"

echo "🎉 Token validation complete!"

# Provide setup instructions if needed
if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ] || [ "$API_RESPONSE" != "200" ]; then
    echo ""
    echo "📖 Setup Instructions:"
    echo "1. Create a GitHub Personal Access Token:"
    echo "   - Go to: https://github.com/settings/tokens"
    echo "   - Create token with 'repo' permissions"
    echo "2. Set environment variable:"
    echo "   export GITHUB_PERSONAL_ACCESS_TOKEN='your_token_here'"
    echo "3. Add to shell profile (e.g., ~/.zshrc or ~/.bashrc):"
    echo "   echo 'export GITHUB_PERSONAL_ACCESS_TOKEN=\"your_token_here\"' >> ~/.zshrc"
fi