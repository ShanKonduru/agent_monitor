@echo off
echo ========================================
echo  PulseGuard Agent Monitor - Quick Deploy
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo 🔍 Checking dependencies...
python -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚡ Installing required packages...
    pip install fastapi uvicorn
    if %errorlevel% neq 0 (
        echo ❌ ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if dashboard file exists
if not exist "web\pulseguard-enterprise-dashboard.html" (
    echo ❌ ERROR: Dashboard file not found
    echo Expected: web\pulseguard-enterprise-dashboard.html
    pause
    exit /b 1
)

echo ✅ All dependencies ready
echo.
echo 🚀 Starting PulseGuard Agent Monitor...
echo 📊 Dashboard will be available at: http://localhost:8000/dashboard
echo 📡 API will be available at: http://localhost:8000/api/v1/agents/
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python working_dashboard_server.py