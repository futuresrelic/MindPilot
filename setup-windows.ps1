# MindPilot Windows Setup Script
# Run this in PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MindPilot Setup for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and run this script again." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Step 1: API Keys Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You need an OpenAI API key to use the AI features." -ForegroundColor Yellow
Write-Host "Already have ChatGPT? Use that same API key!" -ForegroundColor Green
Write-Host "Get your key at: https://platform.openai.com/api-keys" -ForegroundColor Yellow
Write-Host ""

$envFile = ".env"
if (Test-Path $envFile) {
    Write-Host "Found existing .env file" -ForegroundColor Green
    $updateEnv = Read-Host "Do you want to update your API keys? (y/n)"
    if ($updateEnv -eq "y") {
        $apiKey = Read-Host "Enter your OpenAI API key"
        if ($apiKey) {
            (Get-Content $envFile) -replace 'OPENAI_API_KEY=.*', "OPENAI_API_KEY=$apiKey" | Set-Content $envFile
            Write-Host "✓ API key updated" -ForegroundColor Green
        }
    }
} else {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" $envFile -ErrorAction SilentlyContinue
    Write-Host "✓ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Edit the .env file and add your OpenAI API key!" -ForegroundColor Red
    Write-Host "Press any key to open .env file in Notepad..."
    pause
    notepad $envFile
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Step 2: Starting MindPilot" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Docker containers..." -ForegroundColor Yellow
Write-Host "This may take a few minutes on first run..." -ForegroundColor Yellow
Write-Host ""

# Stop any existing containers
docker-compose down 2>$null

# Build and start containers
docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ MindPilot is Running!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "Database: localhost:5432" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Useful Commands:" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "View logs:        docker-compose logs -f" -ForegroundColor Yellow
    Write-Host "Stop MindPilot:   docker-compose down" -ForegroundColor Yellow
    Write-Host "Restart:          docker-compose restart" -ForegroundColor Yellow
    Write-Host "View status:      docker-compose ps" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to view the logs..."
    pause
    docker-compose logs -f
} else {
    Write-Host ""
    Write-Host "✗ Failed to start MindPilot" -ForegroundColor Red
    Write-Host "Check the error messages above." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Docker Desktop not running" -ForegroundColor Yellow
    Write-Host "2. Port 8000 or 5432 already in use" -ForegroundColor Yellow
    Write-Host "3. Missing API key in .env file" -ForegroundColor Yellow
    pause
}
