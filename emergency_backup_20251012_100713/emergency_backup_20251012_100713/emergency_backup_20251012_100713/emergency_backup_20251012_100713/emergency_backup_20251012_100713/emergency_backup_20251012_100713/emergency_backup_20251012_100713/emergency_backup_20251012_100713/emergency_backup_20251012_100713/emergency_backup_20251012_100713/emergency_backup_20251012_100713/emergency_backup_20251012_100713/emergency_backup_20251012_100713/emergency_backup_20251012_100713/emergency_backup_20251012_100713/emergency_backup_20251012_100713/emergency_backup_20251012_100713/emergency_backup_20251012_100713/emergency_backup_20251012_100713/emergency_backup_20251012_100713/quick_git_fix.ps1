# Quick Git fix for immediate push issue

# Check if we have any staged changes
$staged = git diff --cached --name-only
if ($staged) {
    Write-Host "📝 Found staged changes. Committing..." -ForegroundColor Yellow
    git commit -m "Excellence transformation: Market-ready commercial lending platform"
}

# Push to GitHub with explicit branch name
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Blue
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SUCCESS: Commercial-View pushed to GitHub!" -ForegroundColor Green
    Write-Host "🏆 Repository Status: Market-Leading Excellence Achieved" -ForegroundColor Green
} else {
    Write-Host "❌ Push failed. Running diagnostics..." -ForegroundColor Red
    Write-Host "Current branch:" -ForegroundColor Yellow
    git branch
    Write-Host "Remote status:" -ForegroundColor Yellow
    git remote -v
}
