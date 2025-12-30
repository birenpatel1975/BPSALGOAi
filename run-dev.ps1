<#
Run the development server using the repository venv if present.
Usage: .\run-dev.ps1
#>
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $root '.venv\Scripts\python.exe'
if (Test-Path $venvPython) {
    Write-Host "Using venv python: $venvPython"
    & $venvPython (Join-Path $root 'bpsalgoAi\run.py')
} else {
    Write-Host ".venv python not found, using system python"
    python (Join-Path $root 'bpsalgoAi\run.py')
}
