#!/bin/bash

# AI Team Router - Repository Health Check
# Comprehensive verification of repository status and configuration

echo "🏥 Repository Health Check"
echo "=========================="

# Initialize health status
HEALTH_SCORE=100
ISSUES_FOUND=0

# Function to log issues
log_issue() {
    echo "⚠️  $1"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    HEALTH_SCORE=$((HEALTH_SCORE - 10))
}

# Function to log warnings
log_warning() {
    echo "🟡  $1"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    HEALTH_SCORE=$((HEALTH_SCORE - 5))
}

# Function to log success
log_success() {
    echo "✅ $1"
}

# 1. Check Git status
echo "🔍 Git Status Check"
echo "-------------------"

# Check for uncommitted changes
GIT_STATUS=$(git status --porcelain)
if [ -n "$GIT_STATUS" ]; then
    log_issue "Uncommitted changes detected"
    echo "$GIT_STATUS"
else
    log_success "No uncommitted changes"
fi

# Check branch status
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
UPSTREAM_STATUS=$(git rev-parse --abbrev-ref @{u} 2>/dev/null || echo "no upstream")

if [ "$UPSTREAM_STATUS" != "no upstream" ]; then
    AHEAD=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
    BEHIND=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo "0")
    
    if [ "$AHEAD" -gt 0 ]; then
        log_warning "Local branch is $AHEAD commits ahead of remote"
    fi
    
    if [ "$BEHIND" -gt 0 ]; then
        log_warning "Local branch is $BEHIND commits behind remote"
    fi
    
    if [ "$AHEAD" -eq 0 ] && [ "$BEHIND" -eq 0 ]; then
        log_success "Branch is synchronized with remote"
    fi
else
    log_warning "No upstream branch configured"
fi

# 2. Check authentication
echo ""
echo "🔐 Authentication Check"
echo "---------------------"

REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [[ "$REMOTE_URL" == *"https://:@github.com"* ]]; then
    log_issue "Remote URL has empty credentials!"
    echo "🔧 Current URL: $REMOTE_URL"
else
    log_success "Remote URL properly configured"
fi

# Check GitHub token
if [ -n "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    log_success "GitHub token available"
else
    log_warning "No GitHub token in environment"
fi

# 3. Check repository configuration
echo ""
echo "📁 Repository Configuration"
echo "--------------------------"

# Check .gitignore
if [ -f ".gitignore" ]; then
    log_success ".gitignore file exists"
    
    # Check if our HTML file is properly ignored
    if grep -q "inventory-reconciliation-tabs-corrected.html" .gitignore; then
        log_success "Unrelated HTML file properly ignored"
    else
        log_warning "Unrelated HTML file not in .gitignore"
    fi
else
    log_issue ".gitignore file missing!"
fi

# Check hooks directory
if [ -d ".git/hooks" ]; then
    log_success "Git hooks directory exists"
    
    # Check if pre-push hook exists
    if [ -f ".git/hooks/pre-push" ] && [ -x ".git/hooks/pre-push" ]; then
        log_success "Pre-push hook installed and executable"
    else
        log_warning "Pre-push hook missing or not executable"
    fi
else
    log_issue "Git hooks directory missing!"
fi

# 4. Check project files
echo ""
echo "📂 Project Files Check"
echo "---------------------"

# Check main router file
if [ -f "src/ai_team_router.py" ]; then
    log_success "Main router file exists"
else
    log_issue "Main router file missing!"
fi

# Check configuration files
if [ -f "configs/mcp_config.json" ]; then
    log_success "MCP configuration exists"
else
    log_warning "MCP configuration missing"
fi

# Check for sensitive data
SENSITIVE_FILES=$(find . -name "*.env" -o -name "*api_key*" -o -name "*secret*" 2>/dev/null | grep -v ".git" | head -5)
if [ -n "$SENSITIVE_FILES" ]; then
    log_warning "Potential sensitive files found:"
    echo "$SENSITIVE_FILES"
else
    log_success "No obvious sensitive files detected"
fi

# 5. Check scripts directory
echo ""
echo "🛠️ Scripts Check"
echo "----------------"

if [ -d "scripts" ]; then
    log_success "Scripts directory exists"
    
    # Check for our backup script
    if [ -f "scripts/git_config_backup.sh" ] && [ -x "scripts/git_config_backup.sh" ]; then
        log_success "Git config backup script available"
    else
        log_warning "Git config backup script missing"
    fi
    
    # Check for token validation script
    if [ -f "scripts/validate_github_token.sh" ] && [ -x "scripts/validate_github_token.sh" ]; then
        log_success "Token validation script available"
    else
        log_warning "Token validation script missing"
    fi
else
    log_warning "Scripts directory missing"
fi

# 6. Final health assessment
echo ""
echo "📊 Health Assessment"
echo "==================="

if [ "$ISSUES_FOUND" -eq 0 ]; then
    echo "🎉 Repository health: EXCELLENT (100/100)"
    echo "✅ All checks passed - repository is in perfect condition"
elif [ "$ISSUES_FOUND" -lt 3 ]; then
    echo "🟡 Repository health: GOOD ($HEALTH_SCORE/100)"
    echo "⚠️  $ISSUES_FOUND minor issues found - consider fixing"
else
    echo "❌ Repository health: NEEDS ATTENTION ($HEALTH_SCORE/100)"
    echo "⚠️  $ISSUES_FOUND issues found - action recommended"
fi

echo ""
echo "💡 Recommendations:"
echo "- Run: ./scripts/git_config_backup.sh (if authentication issues)"
echo "- Run: ./scripts/validate_github_token.sh (to test token)"
echo "- Check: .gitignore for proper file exclusions"
echo "- Verify: No sensitive data in repository"

echo ""
echo "🎯 Health check complete!"

# Return appropriate exit code
if [ "$ISSUES_FOUND" -gt 0 ]; then
    exit 1
else
    exit 0
fi