@echo off
echo Starting PulseGuard Documentation Server...
echo.
echo Server will run at: http://localhost:8002/documentation-enhanced.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"
python -m http.server 8002