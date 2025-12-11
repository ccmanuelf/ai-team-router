# 🔐 Git Authentication Troubleshooting Guide

## 🚨 Preventing Authentication Issues

This guide helps prevent and resolve Git authentication problems that can cause push failures.

## 🔧 Root Cause Analysis

### Common Issues We've Encountered:

1. **Empty Credentials in Remote URL**
   ```
   https://:@github.com/username/repo.git
   ^^ Empty username/password
   ```

2. **Missing GitHub Personal Access Token**
   - Token not set in environment
   - Token expired or revoked

3. **SSH Key Configuration Issues**
   - No SSH keys configured
   - SSH agent not running

## ✅ Prevention System Implemented

### 1. **Pre-Push Hook** (`.git/hooks/pre-push`)
- **Automatically checks** remote URL before every push
- **Blocks pushes** with empty credentials
- **Provides clear error messages** with solutions

### 2. **Git Configuration Backup** (`scripts/git_config_backup.sh`)
- **Backs up** Git configuration regularly
- **Detects** authentication issues
- **Auto-repairs** when possible

### 3. **Token Validation** (`scripts/validate_github_token.sh`)
- **Validates** GitHub token authenticity
- **Tests** repository access permissions
- **Provides** detailed error diagnostics

### 4. **Health Check** (`scripts/repo_health_check.sh`)
- **Comprehensive** repository status verification
- **Scores** repository health (0-100)
- **Identifies** potential issues before they occur

## 🛠️ Setup Instructions

### 1. Set Up GitHub Personal Access Token

```bash
# Create token at: https://github.com/settings/tokens
# Required permissions: repo (full control)

# Set token in current session
export GITHUB_PERSONAL_ACCESS_TOKEN='ghp_your_token_here'

# Add to shell profile (persistent)
echo 'export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_your_token_here"' >> ~/.zshrc
echo 'export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_your_token_here"' >> ~/.bashrc

# Reload shell
source ~/.zshrc
```

### 2. Configure Git Remote Properly

```bash
# Set remote with token (temporary for push)
git remote set-url origin "https://$GITHUB_PERSONAL_ACCESS_TOKEN@github.com/ccmanuelf/ai-team-router.git"

# After push, reset to normal format
git remote set-url origin "https://github.com/ccmanuelf/ai-team-router.git"
```

### 3. Install Prevention Scripts

```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x .git/hooks/pre-push

# Run initial health check
./scripts/repo_health_check.sh

# Validate token
./scripts/validate_github_token.sh
```

## 🔍 Troubleshooting Steps

### Issue: "Authentication failed for GitHub"

**Diagnosis:**
```bash
# Check current remote URL
git remote -v

# Check for empty credentials
if [[ $(git remote get-url origin) == *"https://:@github.com"* ]]; then
    echo "❌ Empty credentials detected!"
fi
```

**Solution:**
```bash
# Run backup and repair script
./scripts/git_config_backup.sh

# Or manually fix
git remote set-url origin "https://$GITHUB_PERSONAL_ACCESS_TOKEN@github.com/ccmanuelf/ai-team-router.git"
```

### Issue: "Permission denied (publickey)"

**Diagnosis:**
```bash
# Check SSH keys
ls -la ~/.ssh/

# Check if SSH agent is running
eval "$(ssh-agent -s)"
```

**Solution:**
```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to SSH agent
ssh-add ~/.ssh/id_ed25519

# Add to GitHub
# Copy public key and add at: https://github.com/settings/keys
cat ~/.ssh/id_ed25519.pub

# Switch to SSH remote
git remote set-url origin git@github.com:ccmanuelf/ai-team-router.git
```

### Issue: "No GitHub token found"

**Diagnosis:**
```bash
# Check if token is set
echo $GITHUB_PERSONAL_ACCESS_TOKEN

# Check if token is valid
./scripts/validate_github_token.sh
```

**Solution:**
```bash
# Set token
export GITHUB_PERSONAL_ACCESS_TOKEN='ghp_your_token_here'

# Test token
curl -H "Authorization: token $GITHUB_PERSONAL_ACCESS_TOKEN" https://api.github.com/user
```

## 📋 Daily Workflow Checklist

```bash
# 1. Start work session
cd /path/to/ai-team-router

# 2. Check repository health
./scripts/repo_health_check.sh

# 3. Validate token (if needed)
./scripts/validate_github_token.sh

# 4. Do your work...
# ... make changes, commit, etc.

# 5. Before pushing
./scripts/git_config_backup.sh

# 6. Push (pre-push hook will verify)
git push origin main

# 7. End of day backup
./scripts/git_config_backup.sh
```

## 🎯 Best Practices

### ✅ DO:
- **Run health check daily**
- **Validate token weekly**
- **Backup configuration before major changes**
- **Use pre-push hook** (it's automatic)
- **Store token in shell profile** for persistence

### ❌ DON'T:
- **Don't commit tokens** to repository
- **Don't use password authentication** (use tokens or SSH)
- **Don't ignore pre-push warnings**
- **Don't modify .git/hooks** without testing

## 🚀 Recovery Procedures

### Emergency Token Reset

```bash
# 1. Revoke old token on GitHub
# 2. Create new token
# 3. Update environment
export GITHUB_PERSONAL_ACCESS_TOKEN='ghp_new_token_here'

# 4. Update all shell profiles
sed -i '' "s/ghp_old_token/ghp_new_token/g" ~/.zshrc
sed -i '' "s/ghp_old_token/ghp_new_token/g" ~/.bashrc

# 5. Reload
source ~/.zshrc
```

### Complete Reconfiguration

```bash
# 1. Backup current config
./scripts/git_config_backup.sh

# 2. Remove and re-add remote
git remote remove origin
git remote add origin "https://$GITHUB_PERSONAL_ACCESS_TOKEN@github.com/ccmanuelf/ai-team-router.git"

# 3. Test connection
git ls-remote --heads origin main

# 4. Reset to normal URL
git remote set-url origin "https://github.com/ccmanuelf/ai-team-router.git"
```

## 📚 Reference

### GitHub Token Permissions Required:
- `repo` (full control of private repositories)
- `read:org` (optional, for organization access)
- `write:packages` (optional, for GitHub Packages)

### Token Security:
- **Never commit tokens** to version control
- **Use short-lived tokens** when possible
- **Rotate tokens** regularly (every 3-6 months)
- **Revoke immediately** if compromised

### Useful Commands:

```bash
# Check current Git configuration
git config --list

# Check remote URLs
git remote -v

# Test GitHub API access
curl -H "Authorization: token $GITHUB_PERSONAL_ACCESS_TOKEN" https://api.github.com/user

# Check SSH connection
ssh -T git@github.com

# Clear cached credentials
git credential-osxkeychain erase
```

## 🎉 Maintenance Schedule

| Frequency | Task | Command |
|-----------|------|---------|
| **Daily** | Health check | `./scripts/repo_health_check.sh` |
| **Weekly** | Token validation | `./scripts/validate_github_token.sh` |
| **Monthly** | Configuration backup | `./scripts/git_config_backup.sh` |
| **Quarterly** | Token rotation | Create new token, update env |

## 📞 Support

If issues persist:
1. **Run all diagnostic scripts**
2. **Check GitHub status**: https://www.githubstatus.com/
3. **Review this guide** for specific errors
4. **Consult Git documentation**: https://git-scm.com/doc

**Remember:** The pre-push hook will catch most issues before they cause problems!