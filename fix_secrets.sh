#!/bin/bash

# Fix secrets in git history

echo "========================================"
echo "Removing Secrets from Git History"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# First, make sure .env is in .gitignore
echo "📝 Updating .gitignore..."
if ! grep -q "^\.env$" .gitignore; then
    echo ".env" >> .gitignore
    echo "# Environment variables with secrets" >> .gitignore
    echo ".env.*" >> .gitignore
    echo "!.env.example" >> .gitignore
fi

# Create .env.example template (without actual secrets)
echo ""
echo "📄 Creating .env.example template..."
cat > .env.example << 'EOF'
# Environment Variables Template
# Copy this to .env and fill in your actual values

# OpenAI API Key
OPENAI_API_KEY=your_openai_key_here

# Google API
GOOGLE_SHEETS_API_KEY=your_google_sheets_key
GOOGLE_DRIVE_API_KEY=your_google_drive_key

# HubSpot
HUBSPOT_API_KEY=your_hubspot_key

# Slack
SLACK_API_TOKEN=your_slack_token
SLACK_WEBHOOK_URL=your_slack_webhook

# GitHub
GITHUB_TOKEN=your_github_token

# Figma
FIGMA_ACCESS_TOKEN=your_figma_token

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Application
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your_secret_key_here
EOF

# Remove .env from git history
echo ""
echo "🔥 Removing .env from git history..."
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
echo ""
echo "🧹 Cleaning up..."
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "✅ Secrets removed from history!"
echo ""
echo "⚠️  IMPORTANT: Your actual .env file is still on disk (not in git)"
echo ""
echo "Next steps:"
echo "1. Verify .env is not tracked: git status"
echo "2. Force push to update remote: git push origin main --force"
echo "3. Rotate all exposed secrets (OpenAI, Slack, Figma tokens)"
echo ""
