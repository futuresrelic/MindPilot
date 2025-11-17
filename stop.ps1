# Stop MindPilot
Write-Host "Stopping MindPilot..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "✓ MindPilot stopped" -ForegroundColor Green
Write-Host ""
Write-Host "To start again: .\start.ps1" -ForegroundColor Cyan
