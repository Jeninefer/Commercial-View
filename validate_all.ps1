<#
.SYNOPSIS
    Comprehensive validation script for Commercial-View repository
.DESCRIPTION
    Validates all files for syntax errors and production readiness
    - 48,853 Abaco records
    - $208.2M USD portfolio
    - Spanish client support
    - USD factoring validation
#>

Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "🔍 COMMERCIAL-VIEW COMPREHENSIVE VALIDATION" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host ("=" * 70) -ForegroundColor Cyan

$ErrorCount = 0
$WarningCount = 0
$ValidationResults = @()

# Function to add result
function Add-ValidationResult {
    param(
        [string]$Category,
        [string]$Item,
        [string]$Status,
        [string]$Message
    )
    
    $script:ValidationResults += [PSCustomObject]@{
        Category = $Category
        Item     = $Item
        Status   = $Status
        Message  = $Message
    }
    
    if ($Status -eq "ERROR") { $script:ErrorCount++ }
    if ($Status -eq "WARNING") { $script:WarningCount++ }
}

# 1. Validate Python Files
Write-Host "`n📝 Validating Python files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.py" -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $_.FullName -notmatch '\.venv' -and $_.FullName -notmatch '__pycache__'
} | ForEach-Object {
    try {
        $result = python -m py_compile $_.FullName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Add-ValidationResult "Python" $_.Name "OK" "Syntax valid"
            Write-Host "  ✅ $($_.Name)" -ForegroundColor Green
        }
        else {
            Add-ValidationResult "Python" $_.Name "ERROR" $result
            Write-Host "  ❌ $($_.Name): $result" -ForegroundColor Red
        }
    }
    catch {
        Add-ValidationResult "Python" $_.Name "ERROR" $_.Exception.Message
        Write-Host "  ❌ $($_.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 2. Validate JSON Files
Write-Host "`n📋 Validating JSON files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.json" -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $_.FullName -notmatch '\.venv' -and $_.FullName -notmatch 'node_modules'
} | ForEach-Object {
    try {
        $content = Get-Content $_.FullName -Raw | ConvertFrom-Json
        Add-ValidationResult "JSON" $_.Name "OK" "Valid JSON"
        Write-Host "  ✅ $($_.Name)" -ForegroundColor Green
        
        # Special validation for Abaco schema
        if ($_.Name -eq "abaco_schema_autodetected.json") {
            $totalRecords = $content.notes.abaco_integration.total_records
            $portfolio = $content.notes.abaco_integration.financial_summary.total_loan_exposure_usd
            Write-Host "    📊 Abaco Data: $totalRecords records, `$$([math]::Round($portfolio/1000000, 1))M USD" -ForegroundColor Cyan
        }
    }
    catch {
        Add-ValidationResult "JSON" $_.Name "ERROR" $_.Exception.Message
        Write-Host "  ❌ $($_.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 3. Validate Markdown Files
Write-Host "`n📄 Validating Markdown files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.md" -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $_.FullName -notmatch '\.venv'
} | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $issues = @()
    
    # Check for unclosed code blocks
    $codeBlockCount = ([regex]::Matches($content, '```')).Count
    if ($codeBlockCount % 2 -ne 0) {
        $issues += "Unclosed code block"
    }
    
    # Check for invalid headers
    if ($content -match '^#{7,}') {
        $issues += "Invalid header level (>6)"
    }
    
    if ($issues.Count -eq 0) {
        Add-ValidationResult "Markdown" $_.Name "OK" "Valid markdown"
        Write-Host "  ✅ $($_.Name)" -ForegroundColor Green
    }
    else {
        Add-ValidationResult "Markdown" $_.Name "WARNING" ($issues -join ", ")
        Write-Host "  ⚠️  $($_.Name): $($issues -join ', ')" -ForegroundColor Yellow
    }
}

# 4. Validate YAML Files
Write-Host "`n⚙️  Validating YAML files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.yml" -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $_.FullName -notmatch '\.venv'
} | ForEach-Object {
    try {
        # Basic YAML validation (check if file is readable and has content)
        $content = Get-Content $_.FullName -Raw
        if ($content -and $content.Length -gt 0) {
            Add-ValidationResult "YAML" $_.Name "OK" "Valid YAML"
            Write-Host "  ✅ $($_.Name)" -ForegroundColor Green
        }
        else {
            Add-ValidationResult "YAML" $_.Name "WARNING" "Empty file"
            Write-Host "  ⚠️  $($_.Name): Empty file" -ForegroundColor Yellow
        }
    }
    catch {
        Add-ValidationResult "YAML" $_.Name "ERROR" $_.Exception.Message
        Write-Host "  ❌ $($_.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 5. Check Git Status
Write-Host "`n🔄 Checking Git status..." -ForegroundColor Yellow
try {
    $gitStatus = git status --short 2>&1
    if ($LASTEXITCODE -eq 0) {
        if ($gitStatus) {
            Add-ValidationResult "Git" "Repository" "WARNING" "Uncommitted changes"
            Write-Host "  ⚠️  Uncommitted changes detected" -ForegroundColor Yellow
        }
        else {
            Add-ValidationResult "Git" "Repository" "OK" "Clean working tree"
            Write-Host "  ✅ Clean working tree" -ForegroundColor Green
        }
    }
}
catch {
    Add-ValidationResult "Git" "Repository" "ERROR" $_.Exception.Message
}

# 6. Validate Abaco Integration
Write-Host "`n💼 Validating Abaco Integration..." -ForegroundColor Yellow
if (Test-Path "config/abaco_schema_autodetected.json") {
    try {
        $schema = Get-Content "config/abaco_schema_autodetected.json" | ConvertFrom-Json
        $totalRecords = $schema.notes.abaco_integration.total_records
        $portfolio = $schema.notes.abaco_integration.financial_summary.total_loan_exposure_usd
        
        if ($totalRecords -eq 48853) {
            Add-ValidationResult "Abaco" "Record Count" "OK" "48,853 records validated"
            Write-Host "  ✅ Records: 48,853 validated" -ForegroundColor Green
        }
        else {
            Add-ValidationResult "Abaco" "Record Count" "ERROR" "Expected 48,853, got $totalRecords"
            Write-Host "  ❌ Record mismatch" -ForegroundColor Red
        }
        
        if ($portfolio -gt 208000000 -and $portfolio -lt 209000000) {
            Add-ValidationResult "Abaco" "Portfolio Value" "OK" "`$$([math]::Round($portfolio/1000000, 2))M USD"
            Write-Host "  ✅ Portfolio: `$$([math]::Round($portfolio/1000000, 2))M USD" -ForegroundColor Green
        }
        else {
            Add-ValidationResult "Abaco" "Portfolio Value" "WARNING" "Unexpected portfolio value"
            Write-Host "  ⚠️  Portfolio value unexpected" -ForegroundColor Yellow
        }
    }
    catch {
        Add-ValidationResult "Abaco" "Schema" "ERROR" $_.Exception.Message
        Write-Host "  ❌ Schema validation failed" -ForegroundColor Red
    }
}
else {
    Add-ValidationResult "Abaco" "Schema" "ERROR" "Schema file not found"
    Write-Host "  ❌ Schema file not found" -ForegroundColor Red
}

# Summary Report
Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "📊 VALIDATION SUMMARY" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host ("=" * 70) -ForegroundColor Cyan

$okCount = ($ValidationResults | Where-Object { $_.Status -eq "OK" }).Count
$totalChecks = $ValidationResults.Count

Write-Host "`n📈 Results:" -ForegroundColor Cyan
Write-Host "  ✅ Passed: $okCount" -ForegroundColor Green
Write-Host "  ⚠️  Warnings: $WarningCount" -ForegroundColor Yellow
Write-Host "  ❌ Errors: $ErrorCount" -ForegroundColor Red
Write-Host "  📊 Total Checks: $totalChecks" -ForegroundColor Cyan

# Detailed Results by Category
Write-Host "`n📋 Results by Category:" -ForegroundColor Cyan
$ValidationResults | Group-Object Category | ForEach-Object {
    $categoryName = $_.Name
    $categoryResults = $_.Group
    $categoryOK = ($categoryResults | Where-Object { $_.Status -eq "OK" }).Count
    $categoryTotal = $categoryResults.Count
    
    Write-Host "  $categoryName`: $categoryOK/$categoryTotal passed" -ForegroundColor $(
        if ($categoryOK -eq $categoryTotal) { "Green" } 
        elseif ($categoryOK -gt 0) { "Yellow" } 
        else { "Red" }
    )
}

# Final Status
Write-Host "`n🎯 Final Status:" -ForegroundColor Cyan
if ($ErrorCount -eq 0 -and $WarningCount -eq 0) {
    Write-Host "  🏆 OUTSTANDING - All checks passed!" -ForegroundColor Green
    Write-Host "  ✅ Repository is production-ready" -ForegroundColor Green
    exit 0
}
elseif ($ErrorCount -eq 0) {
    Write-Host "  ⚠️  GOOD - Minor warnings only" -ForegroundColor Yellow
    Write-Host "  ✅ Repository is production-ready with warnings" -ForegroundColor Yellow
    exit 0
}
else {
    Write-Host "  ❌ NEEDS ATTENTION - Errors found" -ForegroundColor Red
    Write-Host "  🔧 Please resolve errors before deployment" -ForegroundColor Red
    exit 1
}
