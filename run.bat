@echo off
REM Run the BPSAlgoAI app using the virtualenv python if available
setlocal
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0\bpsalgoAi\run.py" %*
) else (
    echo Virtualenv python not found at "%~dp0.venv\Scripts\python.exe"
    echo Falling back to system python
    python "%~dp0\bpsalgoAi\run.py" %*
)
endlocal
