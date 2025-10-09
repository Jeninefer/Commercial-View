#!/bin/bash

# Remove secrets from git history
# WARNING: This rewrites git history

set -e

echo "========================================"
echo "Removing Secrets from Git History"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# Create backup branch
echo "📦 Creating backup branch..."
git branch backup-before-cleanup-$(date +%Y%m%d) 2>/dev/null || echo "Backup branch already exists"

# Remove .env from entire history
echo ""
echo "🔥 Removing .env from all commits..."
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# Remove refs/original
echo ""
echo "🧹 Cleaning up..."
rm -rf .git/refs/original/

# Expire reflog
git reflog expire --expire=now --all

# Garbage collection
git gc --prune=now --aggressive

echo ""
echo "✅ Secrets removed from history!"
echo ""
echo "⚠️  CRITICAL SECURITY STEPS:"
echo ""
echo "1. Force push to update remote:"
echo "   git push origin main --force"
echo ""
echo "2. IMMEDIATELY rotate these exposed secrets:"
echo "   - OpenAI API Key (https://platform.openai.com/api-keys)"
echo "   - Slack API Token (https://api.slack.com/apps)"
echo "   - Figma Access Token (https://www.figma.com/developers/api#access-tokens)"
echo ""
echo "3. All team members must:"
echo "   git fetch origin"
echo "   git reset --hard origin/main"
echo ""
