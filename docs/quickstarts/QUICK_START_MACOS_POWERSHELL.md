# Quick Start Guide - macOS PowerShell

**You're using**: PowerShell on macOS  
**Repository**: /Users/jenineferderas/Documents/GitHub/Commercial-View  
**Status**: ✅ Already in the correct directory!

---

## ⚠️ Common Mistakes (Don't Do This!)

```powershell

# ❌ DON'T use bash commands in PowerShell

source .venv/bin/activate          # This is bash, not PowerShell!

# ❌ DON'T use Windows paths on macOS

.\.venv\Scripts\Activate.ps1       # Windows path doesn't exist on macOS!

# ❌ DON'T use bare commands (they won't work)

python validate_repository.py      # 'python' not in PATH
pip install -r requirements.txt    # 'pip' not in PATH

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

---

## ✅ Correct Commands for macOS PowerShell

### 1. Activate Virtual Environment

```powershell

# Option 1: Use the activation script (Recommended)

./activate_environment.ps1

# Option 2: Direct activation

& "./.venv/bin/activate"

# Verify activation

& "./.venv/bin/python" --version

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

### 2. Install Dependencies

```powershell

# Install all requirements

& "./.venv/bin/pip" install -r requirements.txt

# Install specific package

& "./.venv/bin/pip" install fastapi uvicorn pandas numpy

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

### 3. Run Scripts

```powershell

# Run validation

& "./.venv/bin/python" validate_repository.py

# Start server

& "./.venv/bin/python" server_control.py

# Run tests

& "./.venv/bin/pytest" tests/

# Generate reports

& "./.venv/bin/python" examples/schema_usage_example.py

# Run Abaco test

& "./.venv/bin/python" scripts/final_abaco_production_test.py

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

### 4. Check Status

```powershell

# Quick status check

& "./.venv/bin/python" scripts/quick_status_check.py

# Repository validation

& "./.venv/bin/python" validate_repository.py

# Git status

git status

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

---

## 🎯 Common Tasks

### Fresh Start

```powershell

# 1. Activate environment

./activate_environment.ps1

# 2. Install/Update dependencies

& "./.venv/bin/pip" install -r requirements.txt --upgrade

# 3. Validate repository

& "./.venv/bin/python" validate_repository.py

# 4. Run tests

& "./.venv/bin/pytest" tests/

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

### Development Workflow

```powershell

# 1. Activate environment

./activate_environment.ps1

# 2. Start development server

& "./.venv/bin/python" server_control.py

# In another terminal, run tests

& "./.venv/bin/pytest" tests/ -v

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

### Production Validation

```powershell

# 1. Run comprehensive validation

& "./.venv/bin/python" scripts/validate_production_data.py

# 2. Run production test

& "./.venv/bin/python" scripts/final_abaco_production_test.py

# 3. Generate production summary

& "./.venv/bin/python" scripts/final_production_summary.py

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

### Git Operations

```powershell

# Check status

git status

# Add and commit

git add .
git commit -m "Your commit message"

# Push to GitHub

git push origin main

# Pull latest

git pull origin main

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

---

## 💡 PowerShell on macOS - Key Differences

| What You Need        | Windows PowerShell             | macOS PowerShell (Unix)      |
| -------------------- | ------------------------------ | ---------------------------- |
| **Virtual Env Path** | `.venv\Scripts\`               | `.venv/bin/`                 |
| **Activate**         | `.\.venv\Scripts\Activate.ps1` | `./activate_environment.ps1` |
| **Python**           | `.\.venv\Scripts\python.exe`   | `& "./.venv/bin/python"`     |
| **Pip**              | `.\.venv\Scripts\pip.exe`      | `& "./.venv/bin/pip"`        |
| **Path Separator**   | `\` (backslash)                | `/` (forward slash)          |
| **Source Command**   | N/A (PowerShell)               | N/A (use `&` in PowerShell)  |

---

## 🔧 Environment Variables

```powershell

# Set environment variables for Abaco

$env:ABACO_RECORDS = "48853"
$env:PORTFOLIO_VALUE = "208192588.65"
$env:PROCESSING_TARGET = "2.3"

# Verify

Write-Host "Records: $env:ABACO_RECORDS"
Write-Host "Portfolio: `$$env:PORTFOLIO_VALUE USD"
Write-Host "Target: $env:PROCESSING_TARGET minutes"

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

---

## 🎯 Quick Reference

```powershell

# Activate environment

./activate_environment.ps1

# Run ANY Python script (template)

& "./.venv/bin/python" <script_name>.py

# Run ANY Python module (template)

& "./.venv/bin/python" -m <module_name>

# Install ANY package (template)

& "./.venv/bin/pip" install <package_name>

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

---

## ✅ Verification

```powershell

# Check if you're in the right directory

Get-Location

# Should output: /Users/jenineferderas/Documents/GitHub/Commercial-View

# Check if virtual environment exists

Test-Path "./.venv/bin/python"

# Should output: True

# Check Python version

& "./.venv/bin/python" --version

# Should output: Python 3.13.7 (or similar)

# Check if dependencies are installed

& "./.venv/bin/pip" list

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

---

## 🚨 Troubleshooting

### Problem: Commands not recognized

```powershell

# ❌ Error: The term 'python' is not recognized

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md

=======
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md
# ✅ Solution: Use full path with &

& "./.venv/bin/python" script.py

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

### Problem: Can't activate environment

```powershell

# ❌ Error: .\.venv\Scripts\Activate.ps1 not found

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md

=======
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md
# ✅ Solution: Use Unix path

./activate_environment.ps1

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

### Problem: Module not found

```powershell

# ❌ Error: No module named 'fastapi'

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md

=======
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md
# ✅ Solution: Install dependencies

& "./.venv/bin/pip" install -r requirements.txt

<<<<<<< Updated upstream:docs/quickstarts/QUICK_START_MACOS_POWERSHELL.md
```bash
=======
```text
>>>>>>> Stashed changes:scripts/QUICK_START_MACOS_POWERSHELL.md

---

## 🎉 Success Checklist

- ✅ You're in `/Users/jenineferderas/Documents/GitHub/Commercial-View`

- ✅ Virtual environment exists at `./.venv/`

- ✅ You can run: `./activate_environment.ps1`

- ✅ You can run: `& "./.venv/bin/python" --version`

- ✅ Dependencies installed: `& "./.venv/bin/pip" list`

**You're ready to work! 🚀**

---

_Quick Reference Updated: October 12, 2024_  
_Platform: macOS with PowerShell_  
_Status: Production Ready ✅_
