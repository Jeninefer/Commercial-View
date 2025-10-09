#!/bin/bash

# Complete cleanup of all issues

set -e

echo "========================================"
echo "Commercial-View Complete Cleanup"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# 1. Backup
echo "📦 Creating backup..."
git branch backup-complete-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true

# 2. Remove .env from history
echo ""
echo "🔥 Removing secrets from history..."
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# 3. Clean up git
echo ""
echo "🧹 Cleaning git repository..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Stage all fixes
echo ""
echo "📝 Staging fixes..."
git add -A

# 5. Commit
echo ""
echo "💾 Committing..."
git commit -m "security: Remove secrets and fix all issues

- Remove .env from git history
- Fix .gitattributes syntax  
- Fix dataclass field ordering
- Fix GitHub workflow YAML
- Update .gitignore
- Clean up src/__init__.py

BREAKING: Git history rewritten. Team must re-clone.
SECURITY: Rotate all exposed secrets immediately." || echo "Nothing to commit"

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "⚠️  CRITICAL: Run these commands now:"
echo ""
echo "1. Force push:"
echo "   git push origin main --force"
echo ""
echo "2. IMMEDIATELY rotate secrets:"
echo "   - OpenAI: https://platform.openai.com/api-keys"
echo "   - Slack: https://api.slack.com/apps"
echo "   - Figma: https://www.figma.com/developers/api#access-tokens"
echo ""
