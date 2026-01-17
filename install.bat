@echo off
SETLOCAL EnableDelayedExpansion

echo ================================================================
echo              ROBOAi Trading Platform Setup
echo             AI-Powered Algorithmic Trading System
echo ================================================================
echo.

:: Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Running without administrator privileges.
    echo Some features may not work correctly.
    echo.
    pause
)

:: Check Python installation
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.10 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% detected
echo.

:: Check Python version (should be 3.10+)
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python 3.10 or higher is required.
    echo Current version: %PYTHON_VERSION%
    echo.
    pause
    exit /b 1
)

:: Prompt for backup
echo [2/8] Backup Configuration
echo.
set /p CREATE_BACKUP="Do you want to create a backup before installation? (Y/N): "
if /i "%CREATE_BACKUP%"=="Y" (
    echo Creating backup...
    set BACKUP_DIR=backups\backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    set BACKUP_DIR=!BACKUP_DIR: =0!
    mkdir "!BACKUP_DIR!" 2>nul
    
    if exist config.yaml (
        copy config.yaml "!BACKUP_DIR!\config.yaml" >nul
        echo [OK] Configuration backed up to !BACKUP_DIR!
    ) else (
        echo [INFO] No existing configuration to backup
    )
    echo.
) else (
    echo [INFO] Skipping backup
    echo.
)

:: Create virtual environment
echo [3/8] Creating virtual environment...
if exist venv (
    echo [INFO] Virtual environment already exists
) else (
    python -m venv venv
    if %errorLevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)
echo.

:: Activate virtual environment
echo [4/8] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

:: Upgrade pip
echo [5/8] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo [OK] Pip upgraded
echo.

:: Install dependencies
echo [6/8] Installing dependencies...
echo This may take several minutes...
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

:: Create config if not exists
echo [7/8] Configuring application...
if not exist config.yaml (
    if exist config.example.yaml (
        copy config.example.yaml config.yaml >nul
        echo [OK] Configuration file created from example
        echo [IMPORTANT] Please edit config.yaml and add your API credentials
    ) else (
        echo [WARNING] config.example.yaml not found
    )
) else (
    echo [INFO] Configuration file already exists
)
echo.

:: Create desktop shortcut
echo [8/8] Creating shortcuts...
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_PATH=%DESKTOP%\ROBOAi Trading.lnk
set SCRIPT_DIR=%~dp0

:: Create a VBS script to create shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%SHORTCUT_PATH%" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_DIR%venv\Scripts\python.exe" >> CreateShortcut.vbs
echo oLink.Arguments = "-m roboai.main" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "ROBOAi Trading Platform" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript CreateShortcut.vbs >nul 2>&1
del CreateShortcut.vbs >nul 2>&1

if exist "%SHORTCUT_PATH%" (
    echo [OK] Desktop shortcut created
) else (
    echo [WARNING] Could not create desktop shortcut
)
echo.

:: Installation complete
echo ================================================================
echo                Installation Complete!
echo ================================================================
echo.

REM Ask about creating additional shortcuts
set /p CREATE_SHORTCUTS="Create additional desktop shortcuts (Dashboard, Start/Stop)? (Y/N): "
if /i "%CREATE_SHORTCUTS%"=="Y" (
    echo.
    call create_shortcuts.bat
)

echo.
echo ================================================================
echo          ROBOAi Trading Platform Ready!
echo ================================================================
echo.
echo Quick Start Options:
echo   [A] Web Dashboard (Recommended):
echo       - Run: start_dashboard.bat (or use desktop shortcut)
echo       - Open: http://localhost:5000 in browser
echo.
echo   [B] Console Mode:
echo       - Run: start_roboai.bat (or use desktop shortcut)
echo.
echo Configuration:
echo   - Edit config.yaml to add your mStock API credentials
echo   - Platform starts in PAPER TRADING mode (safe)
echo.
echo Documentation:
echo   - README.md - Full guide
echo   - DASHBOARD_GUIDE.md - Web dashboard guide
echo   - SHORTCUTS_GUIDE.md - Desktop shortcuts guide
echo.
echo.
echo ================================================================
echo.

set /p LAUNCH_NOW="Do you want to launch the application now? (Y/N): "
if /i "%LAUNCH_NOW%"=="Y" (
    echo.
    echo Launching ROBOAi Trading Platform...
    python -m roboai.main
)

pause
