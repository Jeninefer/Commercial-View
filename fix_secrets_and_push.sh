#!/bin/bash

# Comprehensive script to remove secrets and fix git issues

set -e

echo "========================================"
echo "Fixing Secrets and Git Issues"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# Step 1: Create backup
echo "📦 Creating backup branch..."
git branch backup-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true

# Step 2: Fix .gitattributes (remove comment lines causing warnings)
echo ""
echo "🔧 Fixing .gitattributes..."
cat > .gitattributes << 'EOF'
# Git LFS Configuration

*.csv filter=lfs diff=lfs merge=lfs -text
*.xlsx filter=lfs diff=lfs merge=lfs -text
*.xls filter=lfs diff=lfs merge=lfs -text
*.zip filter=lfs diff=lfs merge=lfs -text
*.tar.gz filter=lfs diff=lfs merge=lfs -text
*.db filter=lfs diff=lfs merge=lfs -text
*.pkl filter=lfs diff=lfs merge=lfs -text
*.pickle filter=lfs diff=lfs merge=lfs -text
EOF

# Step 3: Update .gitignore
echo ""
echo "🔧 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Environment variables - NEVER COMMIT
.env
.env.*
!.env.example

# Credentials
credentials/
*.pem
*.key
service-account*.json
EOF

# Step 4: Remove .env from tracking and history
echo ""
echo "🔥 Removing .env from git..."
git rm --cached .env 2>/dev/null || true

# Remove from all history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# Step 5: Clean up
echo ""
echo "🧹 Cleaning up..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Next: git push origin main --force"
# Step 6: Clean up
echo ""
echo "🧹 Cleaning up git repository..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Step 7: Commit the fixes
echo ""
echo "💾 Committing fixes..."
git add -A
git commit -m "security: Remove secrets and fix git configuration

- Remove .env file from git history
- Fix .gitattributes syntax warnings
- Update .gitignore to exclude sensitive files
- Add .env.example template

SECURITY NOTE: All exposed secrets must be rotated immediately:
- OpenAI API key
- Slack API token
- Figma access token" || echo "Nothing to commit"

echo ""
echo "✅ Repository cleaned successfully!"
echo ""
echo "⚠️  CRITICAL NEXT STEPS:"
echo ""
echo "1. Force push to GitHub:"
echo "   git push origin main --force"
echo ""
echo "2. IMMEDIATELY rotate these exposed secrets:"
echo "   • OpenAI: https://platform.openai.com/api-keys"
echo "   • Slack: https://api.slack.com/apps"
echo "   • Figma: https://www.figma.com/developers/api#access-tokens"
echo ""
echo "3. Create new .env file from template:"
echo "   cp .env.example .env"
echo "   # Then edit .env with your new secrets"
echo ""
echo "4. Notify team members to re-clone or reset:"
echo "   git fetch origin"
echo "   git reset --hard origin/main"
echo ""
