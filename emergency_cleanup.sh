#!/bin/bash
# EMERGENCY API KEY CLEANUP - Remove exposed keys from git history

cd /Users/mcampos.cerda/Documents/Programming/ai-team-router

echo "🚨 EMERGENCY: Removing API keys from git history..."

# Remove validation evidence files with API keys
git filter-branch --force --index-filter \
"git rm --cached --ignore-unmatch validation_evidence/search_tools_validation_*.json" \
--prune-empty --tag-name-filter cat -- --all

# Remove backup file with API keys
git filter-branch --force --index-filter \
"git rm --cached --ignore-unmatch src/ai_team_router_backup.py" \
--prune-empty --tag-name-filter cat -- --all

# Remove temp script
git filter-branch --force --index-filter \
"git rm --cached --ignore-unmatch temp_script.sh" \
--prune-empty --tag-name-filter cat -- --all

# Force garbage collection
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "✅ Git history cleaned"

# Update .gitignore 
cat >> .gitignore << 'EOF'

# API Keys and Sensitive Data
.env
*.key
*api_key*
validation_evidence/*validation*.json
temp_script.sh
*_backup.py

EOF

echo "✅ .gitignore updated"

# Remove local sensitive files
rm -f validation_evidence/search_tools_validation_*.json
rm -f src/ai_team_router_backup.py
rm -f temp_script.sh

echo "✅ Local files removed"
echo "🚨 CRITICAL: Rotate ALL API keys immediately!"
