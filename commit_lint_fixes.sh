#!/bin/bash

# Commit linting fixes

cd "$(dirname "$0")"

echo "Committing linting fixes..."

git add -A

git commit -m "fix: Resolve all linting errors

- Fix src/__init__.py syntax errors
- Fix dataclass field ordering in schema_parser.py
- Fix GitHub workflow CI configuration
- Update schema usage example
- Resolve 200+ Pylance errors
- Clean up type annotations
- Fix import issues"

git push origin main

echo "✅ Linting fixes committed and pushed!"
