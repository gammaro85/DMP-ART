#!/usr/bin/env pwsh
# DMP-ART Portable Startup Script
# Starts the application from the bundled Python runtime without a custom exe.

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  DMP-ART - Portable Mode" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

$pythonCommand = $null

if (Test-Path "runtime\python.exe") {
    $pythonCommand = @("runtime\python.exe", "launcher.py")
    $env:PYTHONHOME = (Join-Path $scriptDir 'runtime')
    $env:PYTHONPATH = (Join-Path $scriptDir 'runtime\Lib\site-packages')
} elseif (Test-Path ".venv\Scripts\python.exe") {
    $pythonCommand = @(".venv\Scripts\python.exe", "launcher.py")
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCommand = @("py", "-3", "launcher.py")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCommand = @("python", "launcher.py")
} else {
    Write-Host "[!] Python runtime not found." -ForegroundColor Red
    Write-Host "    Expected runtime\python.exe or a local Python installation." -ForegroundColor Yellow
    exit 1
}

$env:PYTHONNOUSERSITE = '1'

Write-Host "Starting at: http://localhost:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C in this window to stop the app." -ForegroundColor Gray
Write-Host ""

& $pythonCommand[0] '-s' $pythonCommand[1] $pythonCommand[2]