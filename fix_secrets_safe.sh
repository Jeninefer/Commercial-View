#!/bin/bash

# Safe method to remove secrets using git-filter-repo

echo "========================================"
echo "Safely Removing Secrets from Git History"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# Check if git-filter-repo is installed
if ! command -v git-filter-repo &> /dev/null; then
    echo "Installing git-filter-repo..."
    pip install git-filter-repo
fi

# Backup current state
echo "📦 Creating backup branch..."
git branch backup-before-secret-removal

# Add .env to .gitignore if not already there
echo "📝 Updating .gitignore..."
if ! grep -q "^\.env$" .gitignore; then
    cat >> .gitignore << 'EOF'

# Environment variables with secrets
.env
.env.*
!.env.example
EOF
    git add .gitignore
    git commit -m "chore: Add .env to .gitignore"
fi

# Remove .env from history
echo ""
echo "🔥 Removing .env from git history..."
git filter-repo --path .env --invert-paths --force

echo ""
echo "✅ Secrets removed from history!"
echo ""
echo "⚠️  IMPORTANT SECURITY STEPS:"
echo "1. Your repository history has been rewritten"
echo "2. Force push required: git push origin main --force"
echo "3. All collaborators need to re-clone the repo"
echo "4. IMMEDIATELY rotate these exposed secrets:"
echo "   - OpenAI API Key"
echo "   - Slack API Token"  
echo "   - Figma Personal Access Token"
echo ""
echo "Backup branch created: backup-before-secret-removal"
echo ""
