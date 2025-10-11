#!/bin/bash

echo "🧹 Git Repository Cleanup for Production"
echo "========================================"

# Remove large CSV files from Git tracking
echo "🗑️  Removing large files from Git tracking..."
git rm --cached data/*.csv 2>/dev/null || true
git rm --cached "data/Abaco - Loan Tape_Loan Data_Table.csv" 2>/dev/null || true
git rm --cached "data/Abaco - Loan Tape_Historic Real Payment_Table.csv" 2>/dev/null || true  
git rm --cached "data/Abaco - Loan Tape_Payment Schedule_Table.csv" 2>/dev/null || true

# Update .gitignore
echo "📝 Updating .gitignore..."
cat << 'EOF' > .gitignore
# Large data files - exclude from Git
data/*.csv
data/Abaco*.csv
*.csv
abaco_runtime/exports/**/*.csv

# Temporary files
*.tmp
*.log

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
EOF

echo "✅ Git cleanup complete!"
echo ""
echo "📋 Repository now contains:"
echo "   ✅ Source code and configurations"
echo "   ✅ Documentation and scripts"  
echo "   ✅ Schema files and mappings"
echo "   ❌ Large CSV data files (excluded)"
echo ""
echo "🎯 Ready for clean Git push!"
