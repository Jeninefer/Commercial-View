Write-Host "`n🔧 FIXING INDENTATION ERROR" -ForegroundColor Cyan

$file = "execute_complete_resolution.py"

# Backup
Copy-Item $file "$file.backup"

# Read and fix
$lines = Get-Content $file

# Fix line 815 (adjust index for zero-based array)
$lineIndex = 814  # Line 815 in 0-based array

if ($lines[$lineIndex] -match 'def __str__') {
    # Ensure proper indentation (4 spaces for class method)
    $lines[$lineIndex] = '    def __str__(self) -> str:'
    Write-Host "  ✅ Fixed line 815 indentation" -ForegroundColor Green
}

# Check surrounding lines for context
Write-Host "`nChecking context around line 815:" -ForegroundColor Yellow
for ($i = 810; $i -lt 820; $i++) {
    if ($i -lt $lines.Length) {
        Write-Host "Line $($i+1): $($lines[$i])"
    }
}

# Save fixed file
$lines | Set-Content $file

# Verify
Write-Host "`n🔍 Verifying Python syntax..." -ForegroundColor Yellow
$result = python -m py_compile $file 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Python syntax valid!" -ForegroundColor Green
    
    # Commit
    git add $file
    git commit -m "fix: Resolve IndentationError at line 815"
    git push origin main
    
    Write-Host "`n🏆 Error fixed and committed! 🚀" -ForegroundColor Green
} else {
    Write-Host "  ❌ Syntax error remains: $result" -ForegroundColor Red
    Write-Host "  Restoring backup..." -ForegroundColor Yellow
    Copy-Item "$file.backup" $file
}
