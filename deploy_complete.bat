@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo  PulseGuard Agent Monitor - Complete Deployment Solution
echo ============================================================
echo.

:MENU
echo Choose deployment method:
echo 1. Quick Python Deploy (Fastest - No Docker needed)
echo 2. Docker Deploy (Production-ready containerized)
echo 3. Check Current Status
echo 4. Stop All Services
echo 5. Exit
echo.
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" goto PYTHON_DEPLOY
if "%choice%"=="2" goto DOCKER_DEPLOY
if "%choice%"=="3" goto CHECK_STATUS
if "%choice%"=="4" goto STOP_SERVICES
if "%choice%"=="5" goto EXIT
goto MENU

:PYTHON_DEPLOY
echo.
echo 🐍 Python Deployment Selected
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found
    echo Please install Python 3.11+ from https://python.org
    pause
    goto MENU
)

echo ✅ Python found: 
python --version

REM Check/Install dependencies
echo.
echo 🔍 Checking dependencies...
python -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚡ Installing FastAPI and Uvicorn...
    pip install fastapi uvicorn
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        goto MENU
    )
) else (
    echo ✅ Dependencies already installed
)

REM Check dashboard file
if not exist "web\pulseguard-enterprise-dashboard.html" (
    echo ❌ ERROR: Dashboard file missing
    echo Expected: web\pulseguard-enterprise-dashboard.html
    pause
    goto MENU
)
echo ✅ Dashboard file found

REM Start server
echo.
echo 🚀 Starting PulseGuard Agent Monitor...
echo.
echo 📊 Dashboard: http://localhost:8000/dashboard
echo 📡 API: http://localhost:8000/api/v1/agents/
echo 🤖 AI Metrics: http://localhost:8000/api/v1/system/ai-metrics
echo.
echo Press Ctrl+C to stop
echo.
python working_dashboard_server.py
goto MENU

:DOCKER_DEPLOY
echo.
echo 🐳 Docker Deployment Selected
echo ==============================
echo.

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Docker not found
    echo Please install Docker Desktop
    pause
    goto MENU
)

echo ✅ Docker found:
docker --version

REM Check if already running
docker ps --filter "name=pulseguard-dashboard" --format "table {{.Names}}" | findstr pulseguard-dashboard >nul
if %errorlevel% equ 0 (
    echo ⚠️  PulseGuard is already running
    echo Stopping existing container...
    docker stop pulseguard-dashboard >nul 2>&1
    docker rm pulseguard-dashboard >nul 2>&1
)

echo.
echo 🔨 Building Docker image...
docker build -f Dockerfile.simple -t pulseguard-simple .
if %errorlevel% neq 0 (
    echo ❌ Docker build failed
    pause
    goto MENU
)

echo.
echo 🚀 Starting Docker container...
docker run -d --name pulseguard-dashboard -p 8000:8000 pulseguard-simple
if %errorlevel% neq 0 (
    echo ❌ Failed to start container
    pause
    goto MENU
)

echo.
echo ✅ PulseGuard deployed successfully!
echo.
echo 📊 Dashboard: http://localhost:8000/dashboard
echo 📡 API: http://localhost:8000/api/v1/agents/
echo 🏥 Health: http://localhost:8000/api/v1/health
echo.
echo Container name: pulseguard-dashboard
echo.
pause
goto MENU

:CHECK_STATUS
echo.
echo 🔍 Checking Status...
echo ====================
echo.

REM Check if Python server is running
netstat -an | findstr ":8000" >nul
if %errorlevel% equ 0 (
    echo ✅ Service running on port 8000
    
    REM Test API
    curl -s http://localhost:8000/api/v1/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ API responding
        echo 📊 Dashboard: http://localhost:8000/dashboard
    ) else (
        echo ⚠️  Port 8000 busy but API not responding
    )
) else (
    echo ❌ No service running on port 8000
)

REM Check Docker containers
echo.
echo Docker containers:
docker ps --filter "name=pulseguard" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>nul
if %errorlevel% neq 0 (
    echo No Docker containers running
)

echo.
pause
goto MENU

:STOP_SERVICES
echo.
echo 🛑 Stopping All Services...
echo ===========================
echo.

REM Stop Docker containers
docker stop pulseguard-dashboard >nul 2>&1
docker rm pulseguard-dashboard >nul 2>&1

REM Kill Python processes (be careful with this)
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr "working_dashboard_server" >nul
if %errorlevel% equ 0 (
    echo Stopping Python server...
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq working_dashboard_server*" >nul 2>&1
)

echo ✅ Services stopped
echo.
pause
goto MENU

:EXIT
echo.
echo 👋 Goodbye!
exit /b 0