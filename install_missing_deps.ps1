Write-Host "`n📦 Installing Missing Dependencies" -ForegroundColor Cyan

# Install missing packages
pip install psutil httpx gdown pytest-cov pytest-asyncio

Write-Host "`n✅ All dependencies installed!" -ForegroundColor Green
