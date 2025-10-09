#!/bin/bash

# Commit all improvements made today

set -e

echo "========================================"
echo "Committing Today's Work"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# Check current status
echo "📊 Current git status:"
git status --short

echo ""
read -p "Do you want to commit all these changes? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Commit cancelled"
    exit 1
fi

# Stage all changes
echo ""
echo "📦 Staging all changes..."
git add -A

# Show what will be committed
echo ""
echo "📋 Changes to be committed:"
git status --short

# Create comprehensive commit message
echo ""
echo "💾 Creating commit..."

git commit -m "feat: Major improvements to Commercial-View platform

## Summary
Comprehensive update with security fixes, enhanced functionality,
documentation improvements, and developer experience enhancements.

## Security
- ✅ Removed .env file from entire git history
- ✅ Fixed secret exposure (OpenAI, Slack, Figma tokens)
- ✅ Updated .gitignore to prevent future secret commits
- ✅ Created .env.example template
- ✅ Added security documentation

## Core Improvements
- Enhanced data loader with proper package structure
- Added robust retry mechanism with circuit breaker
- Implemented comprehensive schema parser and analysis tools
- Fixed all Pylance type errors and import issues
- Added proper __init__.py files for clean imports
- Fixed dataclass field ordering issues

## Documentation
- Updated QUICKSTART.md with detailed setup guide
- Enhanced README.md with comprehensive project info
- Added SECURITY_FIX.md with security procedures
- Improved troubleshooting documentation
- Added configuration examples

## Configuration & Setup
- Fixed VS Code settings for Python/TypeScript
- Updated jsconfig.json with proper module resolution
- Enhanced .gitattributes for Git LFS
- Created setup.sh for automated initialization
- Added multiple helper scripts

## Testing & Quality
- Created test suite structure
- Added test_schema_parser.py
- Fixed JavaScript test files (const/let usage)
- Improved code quality (SonarLint fixes)
- Added validation scripts

## Features
- Schema analysis and documentation generation
- Data validation with Pydantic models
- Portfolio analytics pipeline notebook
- Google API integration support
- Enhanced error handling throughout
- Improved logging and monitoring

## Developer Experience
- Created automated setup scripts
- Added requirements.txt and requirements-dev.txt
- Improved git workflow with helper scripts
- Enhanced code organization
- Better error messages

## Files Added/Modified
- setup.sh - Automated project initialization
- fix_secrets_and_push.sh - Secret removal automation
- cleanup_all_issues.sh - Comprehensive cleanup
- SECURITY_FIX.md - Security documentation
- test_schema_parser.py - Schema validation tests
- .env.example - Environment template
- Multiple __init__.py files for proper packaging

## Technical Details
- Python 3.11+ support
- Type hints throughout
- Async/await patterns
- Proper error handling
- Comprehensive logging

## Breaking Changes
- Git history rewritten (secrets removed)
- Team must re-clone repository
- All exposed secrets must be rotated

## Next Steps
- Rotate all exposed API keys
- Enable GitHub secret scanning
- Set up CI/CD pipeline
- Configure monitoring

Closes: Security incident with exposed secrets
Refs: Commercial-View analytics platform improvements
"

echo ""
echo "✅ Changes committed successfully!"
echo ""
echo "📝 Commit details:"
git log -1 --stat

echo ""
echo "🚀 Next steps:"
echo ""
echo "1. Push changes:"
echo "   git push origin main"
echo ""
echo "2. Or force push (if needed):"
echo "   git push origin main --force"
echo ""
echo "3. Verify on GitHub"
echo ""
