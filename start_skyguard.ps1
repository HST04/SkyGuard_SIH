# SkyGuard AI - PowerShell Launcher
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         SkyGuard AI - Multi-Component Launcher          " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend in new window (Standby mode)
Write-Host "[1/2] Starting SkyGuard Backend in STANDBY mode (FastAPI on Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT'; python start_skyguard.py --backend"

# 2. Start Frontend in new window via cmd.exe to avoid PowerShell ExecutionPolicy restrictions on npm
Write-Host "[2/2] Starting Next.js Frontend Dashboard (Port 3000)..." -ForegroundColor Cyan
Start-Process cmd -ArgumentList "/k cd /d `"$ROOT\frontend`" && npm run dev"

Write-Host "`n[OK] SkyGuard AI is ready in STANDBY mode!" -ForegroundColor Green
Write-Host "Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "`nTo generate and stream CSV for video demo:" -ForegroundColor Yellow
Write-Host "  Step 1: python 'SKYGUARD EDGE SIMULATOR\generate_dataset.py' --region mumbai_monsoon --rows 120 --output demo.csv" -ForegroundColor Yellow
Write-Host "  Step 2: python 'SKYGUARD EDGE SIMULATOR\run_simulator.py' --csv demo.csv" -ForegroundColor Yellow
