@echo off
echo Starting Frontend Server...
echo.
cd /d "%~dp0frontend"

echo Opening frontend at http://localhost:8080
echo Press CTRL+C to stop the server
echo.

start http://localhost:8080
python -m http.server 8080
