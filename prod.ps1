#!/usr/bin/env pwsh
# DMP-ART Production Mode Startup Script
# Uruchamia aplikację z gunicorn (produkcja/współdzielenie)

param(
    [int]$Workers = 4,
    [int]$Port = 5000,
    [string]$Host = "0.0.0.0"
)

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  DMP-ART - Production Mode" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[1/4] Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "[!] Virtual environment not found (venv/)" -ForegroundColor Red
    Write-Host "    Run: python -m venv venv" -ForegroundColor Yellow
    Write-Host ""
}

# Check if gunicorn is installed
Write-Host "[2/4] Checking gunicorn installation..." -ForegroundColor Yellow
$gunicornCheck = pip show gunicorn 2>$null
if (-not $gunicornCheck) {
    Write-Host "[!] Gunicorn not installed. Installing..." -ForegroundColor Yellow
    pip install gunicorn
    Write-Host ""
}

# Set production environment variables
Write-Host "[3/4] Setting production environment..." -ForegroundColor Yellow
$env:FLASK_ENV = "production"

# Generate secret key if not set
if (-not $env:SECRET_KEY) {
    Write-Host "[!] SECRET_KEY not set. Generating random key..." -ForegroundColor Yellow
    $env:SECRET_KEY = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    Write-Host "    Save this key for future runs: $env:SECRET_KEY" -ForegroundColor Gray
    Write-Host ""
}

# Start gunicorn server
Write-Host "[4/4] Starting gunicorn server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Server configuration:" -ForegroundColor Green
Write-Host "  Workers: $Workers" -ForegroundColor Gray
Write-Host "  Host: $Host" -ForegroundColor Gray
Write-Host "  Port: $Port" -ForegroundColor Gray
Write-Host "  URL: http://localhost:$Port" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

gunicorn -w $Workers -b "${Host}:${Port}" app:app
