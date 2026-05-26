@echo off
REM DMP-ART Portable Startup Script (CMD version)
REM Starts the application from the bundled Python runtime without a custom exe.

setlocal
cd /d "%~dp0"

echo ==================================
echo   DMP-ART - Portable Mode
echo ==================================
echo.

if exist "runtime\python.exe" (
    set "DMP_ART_PYTHON=runtime\python.exe"
    set "PYTHONHOME=%CD%\runtime"
    set "PYTHONPATH=%CD%\runtime\Lib\site-packages"
) else if exist ".venv\Scripts\python.exe" (
    set "DMP_ART_PYTHON=.venv\Scripts\python.exe"
) else (
    where py >nul 2>&1
    if not errorlevel 1 (
        set "DMP_ART_PYTHON=py -3"
    ) else (
        where python >nul 2>&1
        if not errorlevel 1 (
            set "DMP_ART_PYTHON=python"
        ) else (
            echo [!] Python runtime not found.
            echo     Expected bundled runtime\python.exe or a local Python installation.
            pause
            exit /b 1
        )
    )
)

set "PYTHONNOUSERSITE=1"

echo Starting at: http://localhost:5000
echo Press Ctrl+C in this window to stop the app.
echo.

call %DMP_ART_PYTHON% -s launcher.py

endlocal