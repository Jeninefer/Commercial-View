#!/bin/bash

# Fix Git Rebase Script
cd "$(dirname "$0")"

echo "Fixing git rebase and committing changes..."

# Add all changes
git add .

# Commit with a simple message
git commit -m "Fix: Update schema parser and utilities

- Add proper package structure with __init__.py
- Fix type annotations in schema_parser.py
- Update retry mechanism
- Add test scripts and documentation"

# Continue the rebase
echo ""
echo "Continuing rebase..."
git rebase --continue

echo ""
echo "Checking status..."
git status

echo ""
echo "Done! If rebase is complete, run:"
echo "  git push origin main --force-with-lease"
