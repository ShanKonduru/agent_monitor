@echo off
echo ================================================
echo  PulseGuard Agent Monitor - Deployment Test
echo ================================================
echo.

echo 🧪 Testing deployment requirements...
echo.

REM Test 1: Python availability
echo [1/6] Testing Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ FAIL: Python not found
    goto SUMMARY
) else (
    echo ✅ PASS: Python available
    python --version
)

REM Test 2: Required packages
echo.
echo [2/6] Testing Python packages...
python -c "import fastapi; print('FastAPI:', fastapi.__version__)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  WARN: FastAPI not installed (will auto-install)
) else (
    echo ✅ PASS: FastAPI available
)

python -c "import uvicorn; print('Uvicorn:', uvicorn.__version__)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  WARN: Uvicorn not installed (will auto-install)
) else (
    echo ✅ PASS: Uvicorn available
)

REM Test 3: Dashboard file
echo.
echo [3/6] Testing dashboard files...
if exist "web\pulseguard-enterprise-dashboard.html" (
    echo ✅ PASS: Enhanced dashboard found
    for %%A in ("web\pulseguard-enterprise-dashboard.html") do echo     Size: %%~zA bytes
) else (
    echo ❌ FAIL: Dashboard file missing
)

if exist "working_dashboard_server.py" (
    echo ✅ PASS: Server script found
) else (
    echo ❌ FAIL: Server script missing
)

REM Test 4: Docker availability
echo.
echo [4/6] Testing Docker (optional)...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  WARN: Docker not available (Python deploy only)
) else (
    echo ✅ PASS: Docker available
    docker --version
)

REM Test 5: Port availability
echo.
echo [5/6] Testing port 8000...
netstat -an | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  WARN: Port 8000 is in use
    echo     Current service may need to be stopped
) else (
    echo ✅ PASS: Port 8000 available
)

REM Test 6: Network connectivity (for Docker)
echo.
echo [6/6] Testing network connectivity...
ping -n 1 8.8.8.8 >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  WARN: Network issues detected (Docker may fail)
) else (
    echo ✅ PASS: Network connectivity OK
)

:SUMMARY
echo.
echo ================================================
echo  DEPLOYMENT READINESS SUMMARY
echo ================================================
echo.

if exist "web\pulseguard-enterprise-dashboard.html" if exist "working_dashboard_server.py" (
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ READY FOR PYTHON DEPLOYMENT
        echo.
        echo Quick start: run deploy_simple.bat
        echo Full options: run deploy_complete.bat
    ) else (
        echo ❌ NOT READY: Python required
    )
) else (
    echo ❌ NOT READY: Missing files
)

echo.
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    ping -n 1 8.8.8.8 >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ READY FOR DOCKER DEPLOYMENT
    ) else (
        echo ⚠️  DOCKER: Network issues may cause problems
    )
) else (
    echo ⚠️  DOCKER: Not available
)

echo.
echo Press any key to exit...
pause >nul