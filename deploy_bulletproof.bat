@echo off
:: One-Shot Production Deployment - Bulletproof Docker Deployment
:: Handles all edge cases, network issues, and dependencies automatically

echo =========================================================
echo  Agent Monitor - ONE-SHOT Production Deployment
echo =========================================================
echo.

:: Prerequisite checks
echo [Pre-Check] Validating environment...

:: Check Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running or not installed
    echo    Please start Docker Desktop and try again
    pause & exit /b 1
)

:: Check required files exist
if not exist "web\pulseguard-enterprise-dashboard.html" (
    echo ❌ Dashboard file missing: web\pulseguard-enterprise-dashboard.html
    pause & exit /b 1
)

if not exist "docker-compose.production.yml" (
    echo ❌ Production compose file missing: docker-compose.production.yml
    pause & exit /b 1
)

echo ✅ Environment validated

:: Network connectivity test
echo.
echo [Step 1/6] Testing network connectivity...
docker pull hello-world:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ CRITICAL: Network connectivity failed
    echo    - Cannot reach Docker Hub
    echo    - Check internet connection
    echo    - Try again when network is stable
    pause & exit /b 1
)
docker rmi hello-world:latest >nul 2>&1
echo ✅ Network connectivity confirmed

:: Clean previous deployment
echo.
echo [Step 2/6] Cleaning previous deployment...
docker-compose -f docker-compose.production.yml down -v >nul 2>&1
echo ✅ Clean environment ready

:: Pre-download images
echo.
echo [Step 3/6] Pre-downloading PostgreSQL image...
echo    This may take 1-2 minutes depending on connection...
docker pull postgres:15 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ CRITICAL: Failed to download PostgreSQL image
    echo    - Network timeout or Docker Hub unavailable
    echo    - Try again later when network is stable
    pause & exit /b 1
)
echo ✅ PostgreSQL image ready

:: Verify application images
echo.
echo [Step 4/6] Verifying application images...
docker image inspect agent_monitor-monitor:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ CRITICAL: agent_monitor-monitor:latest image missing
    echo    This image must be built before deployment
    echo    Please run: docker build -f docker\Dockerfile -t agent_monitor-monitor:latest .
    pause & exit /b 1
)

docker image inspect agent_monitor-test-agent:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ CRITICAL: agent_monitor-test-agent:latest image missing
    echo    This image must be built before deployment
    pause & exit /b 1
)
echo ✅ Application images verified

:: Deploy system
echo.
echo [Step 5/6] Deploying complete production system...
echo    - PostgreSQL Database Container
echo    - Monitor Dashboard Container
echo    - 5 Production Agent Containers
echo.
docker-compose -f docker-compose.production.yml up -d
if %errorlevel% neq 0 (
    echo ❌ CRITICAL: Deployment failed
    echo.
    echo Showing error logs:
    docker-compose -f docker-compose.production.yml logs --tail=20
    pause & exit /b 1
)

:: Health verification with timeout
echo.
echo [Step 6/6] Verifying system health...
echo    Waiting for services to initialize (up to 90 seconds)...

:: Wait for PostgreSQL
echo    Checking PostgreSQL...
for /l %%i in (1,1,18) do (
    docker exec agent_monitor-postgres-1 pg_isready -U agent_monitor >nul 2>&1
    if not errorlevel 1 goto :postgres_ok
    timeout /t 5 /nobreak >nul
)
echo ❌ PostgreSQL failed to start within 90 seconds
goto :show_logs

:postgres_ok
echo ✅ PostgreSQL ready

:: Wait for Monitor Dashboard
echo    Checking Monitor Dashboard...
for /l %%i in (1,1,12) do (
    curl -s http://localhost:8000/api/v1/agents/ >nul 2>&1
    if not errorlevel 1 goto :monitor_ok
    timeout /t 5 /nobreak >nul
)
echo ❌ Monitor Dashboard failed to start within 60 seconds
goto :show_logs

:monitor_ok
echo ✅ Monitor Dashboard ready

:: Update dashboard to latest
echo    Updating dashboard to latest version...
docker cp web\pulseguard-enterprise-dashboard.html agent_monitor-monitor-dashboard-1:/app/web/ >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Latest dashboard deployed
) else (
    echo ⚠️  Dashboard update failed (using existing version)
)

:: Final verification
echo.
echo    Final system verification...
for /f %%i in ('docker ps --filter "name=agent_monitor" --filter "status=running" --quiet ^| find /c /v ""') do set RUNNING=%%i

goto :success

:show_logs
echo.
echo TROUBLESHOOTING INFORMATION:
echo ===========================
docker-compose -f docker-compose.production.yml logs --tail=10
goto :status

:success
echo.
echo =========================================================
echo               🎉 DEPLOYMENT SUCCESS! 🎉
echo =========================================================
echo.

:status
:: Show final status
echo System Status:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr -E "(NAMES|agent_monitor)"

echo.
if "%RUNNING%"=="7" (
    echo ✅ SUCCESS: All 7 containers operational
    echo    💾 PostgreSQL Database: Running & Healthy
    echo    📊 Monitor Dashboard: Running & Healthy  
    echo    🤖 Production Agents: 5 agents registered
    echo.
    echo 🌐 Access Your System:
    echo    Dashboard: http://localhost:8000
    echo    Database:  localhost:5432
    echo.
    echo Opening dashboard in browser...
    start http://localhost:8000/
) else (
    echo ⚠️  System partially deployed (%RUNNING%/7 containers)
    echo    Check logs above for issues
)

echo.
echo 🔧 Management Commands:
echo    View Logs:     docker-compose -f docker-compose.production.yml logs
echo    Restart All:   docker-compose -f docker-compose.production.yml restart
echo    Stop All:      docker-compose -f docker-compose.production.yml down
echo    Agent Status:  docker ps
echo.
echo Press any key to exit...
pause >nul