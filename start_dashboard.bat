@echo off
REM ROBOAi Web Dashboard - Start Script for Windows

echo ================================================================
echo          ROBOAi Trading Platform - Web Dashboard
echo ================================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/2] Activating virtual environment...
call venv\Scripts\activate.bat

REM Start the web dashboard
echo [2/2] Starting web dashboard...
echo.
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
echo ================================================================
echo.

python start_dashboard.py

pause
