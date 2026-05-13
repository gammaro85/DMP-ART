@echo off
REM DMP-ART Production Mode Startup Script (CMD version)
REM Uruchamia aplikację z gunicorn (produkcja/współdzielenie)

echo ==================================
echo   DMP-ART - Production Mode
echo ==================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [1/4] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [!] Virtual environment not found (venv/)
    echo     Run: python -m venv venv
    echo.
)

REM Check if gunicorn is installed
echo [2/4] Checking gunicorn installation...
pip show gunicorn >nul 2>&1
if errorlevel 1 (
    echo [!] Gunicorn not installed. Installing...
    pip install gunicorn
    echo.
)

REM Set production environment variables
echo [3/4] Setting production environment...
set FLASK_ENV=production

REM Generate secret key if not set
if not defined SECRET_KEY (
    echo [!] SECRET_KEY not set. Using default key...
    echo     Set SECRET_KEY environment variable for production!
    set SECRET_KEY=change-this-secret-key-in-production
    echo.
)

REM Start gunicorn server
echo [4/4] Starting gunicorn server...
echo.
echo Server configuration:
echo   Workers: 4
echo   Host: 0.0.0.0
echo   Port: 5000
echo   URL: http://localhost:5000
echo.
echo Press Ctrl+C to stop
echo.

gunicorn -w 4 -b 0.0.0.0:5000 app:app
