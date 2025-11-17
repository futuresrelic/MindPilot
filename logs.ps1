# View MindPilot logs
Write-Host "Viewing MindPilot logs..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop viewing" -ForegroundColor Yellow
Write-Host ""
docker-compose logs -f
