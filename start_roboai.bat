@echo off
REM ROBOAi Trading Platform - Start Script for Windows

echo ================================================================
echo              ROBOAi Trading Platform - Starting
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
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if config exists
if not exist "config.yaml" (
    echo [WARNING] config.yaml not found!
    echo Creating from example...
    copy config.example.yaml config.yaml >nul
    echo [INFO] Please edit config.yaml before using live trading.
    echo.
)

REM Display mode
echo [2/3] Checking configuration...
python -c "from roboai.utils import get_config; c = get_config(); print(f'Trading Mode: {c.get(\"trading.mode\")}')" 2>nul
if %errorLevel% neq 0 (
    echo [WARNING] Could not read config, will use defaults
)
echo.

REM Start the platform
echo [3/3] Starting ROBOAi Trading Platform...
echo Press Ctrl+C to stop the platform
echo.
echo ================================================================
echo.

python -m roboai.main

REM Platform stopped
echo.
echo ================================================================
echo              ROBOAi Trading Platform - Stopped
echo ================================================================
echo.
pause
