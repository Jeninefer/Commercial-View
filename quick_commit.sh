#!/bin/bash

# Quick commit script for Commercial-View

cd "$(dirname "$0")"

# Stage all changes
git add .

# Commit with a concise message
git commit -m "feat: Update project structure and documentation

- Enhanced data loader and schema parser
- Fixed import issues and type errors  
- Updated documentation (QUICKSTART.md, README.md)
- Added setup automation scripts
- Improved VS Code configuration
- Fixed test suite issues"

echo "✅ Changes committed!"
echo ""
echo "To push: git push origin main --force-with-lease"
