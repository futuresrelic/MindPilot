# Quick start script for MindPilot
Write-Host "Starting MindPilot..." -ForegroundColor Cyan
docker-compose up -d

Write-Host ""
Write-Host "✓ MindPilot is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs:    http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "View logs:   docker-compose logs -f" -ForegroundColor Yellow
Write-Host "Stop:        docker-compose down" -ForegroundColor Yellow
