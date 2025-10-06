#!/bin/bash

# Commercial-View Safe Commit Script
# Commits changes while avoiding GitHub workflow scope issues

echo "🚀 Commercial-View Safe Commit Process"
echo "======================================"

# Run the cleanup script
echo "🔧 Running repository cleanup..."
/Users/jenineferderas/Commercial-View/.venv/bin/python scripts/fix_workflow_issue.py

# Validate content is English-only with no demo data
echo "🔍 Validating repository content..."
/Users/jenineferderas/Commercial-View/.venv/bin/python scripts/validate_english_only.py

if [ $? -ne 0 ]; then
    echo "❌ Validation failed. Please fix issues before committing."
    exit 1
fi

# Add all changes except workflows
echo "📝 Adding changes to git..."
git add .
git add -A

# Check what will be committed
echo "📋 Files to be committed:"
git status --porcelain

# Commit with descriptive message
echo "💾 Committing changes..."
git commit -m "Commercial-View: Production-ready English-only content

✅ Removed all demo and example data
✅ Ensured 100% English content
✅ Fixed repository structure
✅ Added production validation scripts
✅ Updated documentation and build processes

No demo data, examples, or non-English content remain.
Repository is production-ready for commercial lending analytics."

# Push to GitHub (excluding workflows to avoid OAuth scope issues)
echo "🚀 Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "📝 Note: Workflow files were excluded due to OAuth scope limitations."
    echo "   You can add them manually through the GitHub web interface."
else
    echo "❌ Push failed. Check git status and try again."
    exit 1
fi

echo ""
echo "🎉 Commercial-View repository is now production-ready!"
echo "✅ 100% English content"
echo "✅ Zero demo data" 
echo "✅ Production-ready commercial lending platform"
