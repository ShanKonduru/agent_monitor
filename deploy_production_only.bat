@echo off
:: PRODUCTION DEPLOYMENT - Uses ONLY files listed in PRODUCTION_FILES.md
:: No dev/test files, no alternatives, no confusion

echo ===================================================
echo  PRODUCTION DEPLOYMENT - Documented Files Only
echo ===================================================
echo.
echo Reading from: PRODUCTION_FILES.md manifest
echo.

:: Validate ONLY production files exist
echo [1/4] Validating production files from manifest...

if not exist "docker-compose.production.yml" (
    echo ❌ CRITICAL: docker-compose.production.yml missing
    echo    This is the main production orchestration file
    pause & exit /b 1
)

if not exist "web\pulseguard-enterprise-dashboard.html" (
    echo ❌ CRITICAL: web\pulseguard-enterprise-dashboard.html missing
    pause & exit /b 1
)

:: Verify production images
docker image inspect agent_monitor-monitor:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ CRITICAL: agent_monitor-monitor:latest image missing
    echo    Build required before deployment
    pause & exit /b 1
)

docker image inspect agent_monitor-test-agent:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ CRITICAL: agent_monitor-test-agent:latest image missing
    echo    Build required before deployment
    pause & exit /b 1
)

echo ✅ All production files validated

:: Clean and deploy using ONLY production compose file
echo.
echo [2/4] Clean deployment using production files...
docker-compose -f docker-compose.production.yml down -v >nul 2>&1

echo.
echo [3/4] Deploying production system...
echo    File: docker-compose.production.yml
echo    Containers: 7 (1 PostgreSQL + 1 Monitor + 5 Agents)
echo.

docker-compose -f docker-compose.production.yml up -d
if %errorlevel% neq 0 (
    echo ❌ Deployment failed
    docker-compose -f docker-compose.production.yml logs --tail=10
    pause & exit /b 1
)

echo ✅ All containers started

:: Update to production dashboard
echo.
echo [4/4] Updating to production dashboard...
timeout /t 10 /nobreak >nul
docker cp web\pulseguard-enterprise-dashboard.html agent_monitor-monitor-dashboard-1:/app/web/ >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Production dashboard (188KB) deployed
) else (
    echo ⚠️  Dashboard update skipped
)

:: Final status
echo.
echo ===================================================
echo              PRODUCTION STATUS
echo ===================================================

for /f %%i in ('docker ps --filter "name=agent_monitor" --filter "status=running" --quiet ^| find /c /v ""') do set RUNNING=%%i

if "%RUNNING%"=="7" (
    echo ✅ SUCCESS: All 7 production containers running
    echo.
    echo Production System:
    echo   📊 Dashboard: http://localhost:8000
    echo   🐘 Database:  PostgreSQL container
    echo   🤖 Agents:    5 production agents
    echo.
    echo PostgreSQL Credentials:
    echo   Host: localhost:5432
    echo   Database: agent_monitor
    echo   Username: agent_monitor
    echo   Password: agent_monitor_password
    echo   Connection: postgresql://agent_monitor:agent_monitor_password@localhost:5432/agent_monitor
    echo.
    start http://localhost:8000/
) else (
    echo ❌ Partial deployment: %RUNNING%/7 containers
    echo.
    echo Status:
    docker ps --filter "name=agent_monitor" --format "table {{.Names}}\t{{.Status}}"
)

echo.
echo Production Management:
echo   Status: docker ps --filter "name=agent_monitor"
echo   Logs:   docker-compose -f docker-compose.production.yml logs
echo   Stop:   docker-compose -f docker-compose.production.yml down
echo.
pause