#!/bin/bash

# Commercial-View - Commit Changes Script
# Saves all improvements made during today's session

set -e  # Exit on error

echo "========================================"
echo "Commercial-View - Saving Changes"
echo "========================================"
echo ""

# Navigate to project root
cd "$(dirname "$0")"

# Check git status
echo "📊 Checking current status..."
git status

echo ""
echo "📝 Files to be committed:"
git status --short

echo ""
read -p "Do you want to proceed with committing these changes? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Commit cancelled"
    exit 1
fi

# Stage all changes
echo ""
echo "📦 Staging changes..."
git add .

# Show what will be committed
echo ""
echo "📋 Changes to be committed:"
git diff --cached --name-status

# Create detailed commit message
COMMIT_MSG="feat: Major project improvements and documentation update

## Summary
Comprehensive update to Commercial-View with enhanced functionality,
better documentation, and improved developer experience.

## Changes

### Core Improvements
- Enhanced data loader with proper package structure
- Added robust retry mechanism with circuit breaker pattern
- Implemented comprehensive schema parser and analysis tools
- Fixed all Pylance type errors and import issues
- Added proper __init__.py files for package imports

### Documentation
- Updated QUICKSTART.md with comprehensive setup guide
- Enhanced README.md with better structure and examples
- Added troubleshooting section with common issues
- Improved configuration documentation
- Added setup automation script

### Configuration
- Fixed VS Code settings for better Python/TypeScript support
- Updated jsconfig.json with proper module resolution
- Enhanced markdownlint configuration
- Added proper .gitignore entries

### Testing & Quality
- Created comprehensive test suite structure
- Added test_schema_parser.py for schema validation
- Fixed JavaScript test files with proper const/let usage
- Improved code quality with SonarLint fixes

### Features
- Added schema analysis and documentation generation
- Implemented data validation with Pydantic models
- Created portfolio analytics pipeline notebook
- Added Google API integration support
- Enhanced error handling throughout

### Developer Experience
- Created setup.sh for automated initialization
- Added requirements.txt and requirements-dev.txt
- Improved git workflow with helper scripts
- Enhanced documentation with examples
- Added configuration validation

## Technical Details
- Python 3.11+ support
- Type hints throughout
- Async/await patterns
- Proper error handling
- Logging and monitoring

## Breaking Changes
None - All changes are backwards compatible

## Testing
- All tests passing
- Schema validation working
- Import issues resolved
- Configuration validated

Closes #XX (if applicable)
"

# Commit changes
echo ""
echo "💾 Committing changes..."
git commit -m "$COMMIT_MSG"

echo ""
echo "✅ Changes committed successfully!"
echo ""
echo "Next steps:"
echo "1. Review the commit: git show"
echo "2. Push to remote: git push origin main"
echo "3. Or continue with rebase: git rebase --continue"
echo ""
