@echo off
REM ROBOAi Trading Platform - Stop Script for Windows

echo ================================================================
echo              ROBOAi Trading Platform - Stopping
echo ================================================================
echo.

echo Looking for ROBOAi processes...
echo.

REM Find Python processes running roboai
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr /I "PID"') do (
    set PID=%%i
    echo Found Python process: !PID!
    
    REM Check if it's running roboai
    wmic process where "ProcessId=!PID!" get CommandLine 2>nul | findstr /I "roboai" >nul
    if !errorLevel! equ 0 (
        echo Stopping ROBOAi process !PID!...
        taskkill /PID !PID! /F
        echo Process stopped.
    )
)

echo.
echo ================================================================
echo              ROBOAi Trading Platform - Stopped
echo ================================================================
echo.
pause
