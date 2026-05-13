#!/usr/bin/env pwsh
# DMP-ART Development Mode Startup Script
# Uruchamia aplikację w trybie deweloperskim z auto-reload

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  DMP-ART - Developer Mode" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[1/3] Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "[!] Virtual environment not found (venv/)" -ForegroundColor Red
    Write-Host "    Run: python -m venv venv" -ForegroundColor Yellow
    Write-Host ""
}

# Set development environment variables
Write-Host "[2/3] Setting development environment..." -ForegroundColor Yellow
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "1"

# Start Flask development server
Write-Host "[3/3] Starting Flask development server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Server starting at: http://localhost:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

python app.py
