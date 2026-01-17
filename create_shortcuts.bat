@echo off
REM ROBOAi - Create Desktop Shortcuts for Windows

echo ================================================================
echo        Creating ROBOAi Desktop Shortcuts
echo ================================================================
echo.

SET SCRIPT_DIR=%~dp0
SET SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

echo Creating shortcuts on desktop...
echo.

REM Create Start Platform shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\ROBOAi - Start Platform.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_DIR%\start_roboai.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Start ROBOAi Trading Platform" >> CreateShortcut.vbs
echo oLink.IconLocation = "%%SystemRoot%%\System32\SHELL32.dll,137" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs
echo [OK] Created: ROBOAi - Start Platform.lnk

REM Create Stop Platform shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\ROBOAi - Stop Platform.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_DIR%\stop_roboai.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Stop ROBOAi Trading Platform" >> CreateShortcut.vbs
echo oLink.IconLocation = "%%SystemRoot%%\System32\SHELL32.dll,131" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs
echo [OK] Created: ROBOAi - Stop Platform.lnk

REM Create Start Dashboard shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\ROBOAi - Dashboard.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_DIR%\start_dashboard.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Start ROBOAi Web Dashboard" >> CreateShortcut.vbs
echo oLink.IconLocation = "%%SystemRoot%%\System32\SHELL32.dll,14" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs
echo [OK] Created: ROBOAi - Dashboard.lnk

REM Create Open Dashboard URL shortcut
echo [InternetShortcut] > "%USERPROFILE%\Desktop\ROBOAi - Open Dashboard.url"
echo URL=http://localhost:5000 >> "%USERPROFILE%\Desktop\ROBOAi - Open Dashboard.url"
echo IconIndex=0 >> "%USERPROFILE%\Desktop\ROBOAi - Open Dashboard.url"
echo IconFile=%%SystemRoot%%\System32\SHELL32.dll >> "%USERPROFILE%\Desktop\ROBOAi - Open Dashboard.url"
echo [OK] Created: ROBOAi - Open Dashboard.url

echo.
echo ================================================================
echo                   Shortcuts Created!
echo ================================================================
echo.
echo Desktop shortcuts created:
echo   1. ROBOAi - Start Platform.lnk
echo   2. ROBOAi - Stop Platform.lnk
echo   3. ROBOAi - Dashboard.lnk
echo   4. ROBOAi - Open Dashboard.url
echo.
echo You can now start/stop the platform from your desktop!
echo.
pause
