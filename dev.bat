@echo off
REM DMP-ART Development Mode Startup Script (CMD version)
REM Uruchamia aplikację w trybie deweloperskim z auto-reload

echo ==================================
echo   DMP-ART - Developer Mode
echo ==================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [1/3] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [!] Virtual environment not found (venv/)
    echo     Run: python -m venv venv
    echo.
)

REM Set development environment variables
echo [2/3] Setting development environment...
set FLASK_ENV=development
set FLASK_DEBUG=1

REM Start Flask development server
echo [3/3] Starting Flask development server...
echo.
echo Server starting at: http://localhost:5000
echo Press Ctrl+C to stop
echo.

python app.py
