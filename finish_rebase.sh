#!/bin/bash

# Finish the current rebase and push changes

cd "$(dirname "$0")"

echo "========================================"
echo "Finishing Git Rebase"
echo "========================================"
echo ""

# Stage all changes
echo "📦 Staging all changes..."
git add .

# Commit
echo "💾 Committing changes..."
git commit -m "feat: Project improvements - schema parser, docs, and fixes

- Add comprehensive schema parser with validation
- Fix all import and type errors
- Update documentation and setup guides  
- Enhance VS Code configuration
- Add test suite and examples
- Improve error handling and retry logic"

# Continue rebase
echo ""
echo "⏭️  Continuing rebase..."
git rebase --continue

# Check if rebase is complete
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Rebase completed successfully!"
    echo ""
    echo "Next step: Push to remote"
    echo "  git push origin main --force-with-lease"
else
    echo ""
    echo "⚠️  Rebase not complete. Check status:"
    echo "  git status"
fi
