@echo off
echo Starting Lab Test Optimization System Backend...
echo.
cd /d "%~dp0backend"

REM Check if .env exists
if not exist "..\. env" (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and add your Groq API key
    pause
    exit /b 1
)

echo Starting FastAPI server on http://localhost:8000
echo Press CTRL+C to stop the server
echo.

python main.py
