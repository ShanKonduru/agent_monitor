@echo off
:: Pre-deployment System Validator
:: Checks all requirements before attempting deployment

echo ================================================
echo  Pre-Deployment System Validation
echo ================================================
echo.

set "errors=0"

:: Docker availability
echo [Check 1/8] Docker availability...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not available
    set /a errors+=1
) else (
    echo ✅ Docker running
)

:: Network connectivity
echo.
echo [Check 2/8] Network connectivity...
ping -n 1 8.8.8.8 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ No internet connectivity
    set /a errors+=1
) else (
    echo ✅ Internet available
)

:: Docker Hub access
echo.
echo [Check 3/8] Docker Hub access...
docker pull hello-world:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Cannot reach Docker Hub
    set /a errors+=1
) else (
    echo ✅ Docker Hub accessible
    docker rmi hello-world:latest >nul 2>&1
)

:: Required files
echo.
echo [Check 4/8] Required files...
if not exist "docker-compose.production.yml" (
    echo ❌ Missing: docker-compose.production.yml
    set /a errors+=1
) else (
    echo ✅ Production compose file present
)

if not exist "web\pulseguard-enterprise-dashboard.html" (
    echo ❌ Missing: web\pulseguard-enterprise-dashboard.html
    set /a errors+=1
) else (
    for %%i in ("web\pulseguard-enterprise-dashboard.html") do (
        if %%~zi LSS 100000 (
            echo ❌ Dashboard file too small: %%~zi bytes
            set /a errors+=1
        ) else (
            echo ✅ Dashboard file present: %%~zi bytes
        )
    )
)

:: Application images
echo.
echo [Check 5/8] Application images...
docker image inspect agent_monitor-monitor:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Missing: agent_monitor-monitor:latest
    set /a errors+=1
) else (
    echo ✅ Monitor image available
)

docker image inspect agent_monitor-test-agent:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Missing: agent_monitor-test-agent:latest
    set /a errors+=1
) else (
    echo ✅ Agent image available
)

:: Port availability
echo.
echo [Check 6/8] Port availability...
netstat -an | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Port 8000 in use (will stop existing service)
) else (
    echo ✅ Port 8000 available
)

netstat -an | findstr ":5432" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Port 5432 in use (PostgreSQL may conflict)
) else (
    echo ✅ Port 5432 available
)

:: Docker resources
echo.
echo [Check 7/8] Docker resources...
for /f "tokens=4" %%i in ('docker system df ^| findstr "Local Volumes"') do set "volumes=%%i"
if "%volumes%" GTR "50" (
    echo ⚠️  Many Docker volumes: %volumes% (consider cleanup)
) else (
    echo ✅ Docker volumes manageable
)

:: System readiness
echo.
echo [Check 8/8] Overall readiness...
if %errors% equ 0 (
    echo ✅ System ready for deployment
    echo.
    echo ================================================
    echo           ✅ ALL CHECKS PASSED ✅
    echo ================================================
    echo.
    echo Your system is ready for bulletproof deployment.
    echo Run: deploy_bulletproof.bat
    echo.
) else (
    echo ❌ System not ready: %errors% issues found
    echo.
    echo ================================================
    echo         ❌ DEPLOYMENT NOT RECOMMENDED ❌
    echo ================================================
    echo.
    echo Please resolve the issues above before deployment.
    echo.
)

pause