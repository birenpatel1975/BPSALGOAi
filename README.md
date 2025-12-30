# BPSALGOAi
NSE F&amp;O Ai Trading

## activate vnv:
& D:\BPSALGOAi\BPSALGOAi\.venv\Scripts\Activate.ps1

## run py project
python run.py

## Or run without activating:
D:\BPSALGOAi\BPSALGOAi\.venv\Scripts\python.exe run.py

## Alternative (Flask CLI):
$env:FLASK_APP='run.py'
$env:FLASK_ENV='development'
flask run --host=0.0.0.0 --port=5000

## Browser Preview
http://localhost:5000.
