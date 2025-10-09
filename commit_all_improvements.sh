#!/bin/bash

# Commit all code quality improvements

cd "$(dirname "$0")"

echo "=========================================="
echo "Committing All Code Quality Improvements"
echo "=========================================="
echo ""

git add -A

git commit -m "refactor: Code quality improvements and linting fixes

Security & Quality:
- Fix CWE-546: Add missing Request import
- Replace duplicate string literals with constants (SonarLint S1192)
- Add column name constants from schema
- Fix unused variable assignments (SonarLint S1854)
- Improve type safety with proper imports

Code Organization:
- Consolidate all status constants
- Add dataset name constants
- Add schema column constants
- Improve code maintainability

API Improvements:
- Better error handling
- Consistent status messages
- Schema-aligned column definitions
- Improved logging

Testing:
- All linting errors resolved
- Security warnings fixed
- Code complexity reduced
- Type hints improved

Files Modified:
- run.py - Major refactoring and improvements
- src/__init__.py - Fixed syntax errors
- src/utils/schema_parser.py - Fixed dataclass ordering
- examples/schema_usage_example.py - Fixed attribute access
- .github/workflows/ci.yml - Fixed YAML syntax

Breaking Changes: None
Backward Compatible: Yes"

echo ""
echo "✅ Changes committed!"
echo ""
echo "Next: git push origin main"
