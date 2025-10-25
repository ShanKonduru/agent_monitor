@echo off
chcp 65001 >nul
:: ENHANCED ROBUST DEPLOYMENT - Addresses all edge cases
:: Handles network issues, port conflicts, missing images, and resource constraints

echo =========================================================
echo  ENHANCED ROBUST PRODUCTION DEPLOYMENT
echo =========================================================
echo.

# Advanced validation with fallback strategies
echo [1/6] Comprehensive System Validation...

:: Check Docker resources
echo    Checking Docker system status...
docker system df >nul 2>&1
if %errorlevel% equ 0 (
    echo    Docker system operational
) else (
    echo    WARNING: Docker system check failed
)

:: Check available memory using PowerShell
echo    Checking system resources...
for /f %%i in ('powershell -Command "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB -as [int]"') do set mem_gb=%%i
if defined mem_gb (
    if %mem_gb% LSS 4 (
        echo    WARNING: Low system memory: %mem_gb%GB (recommend 4GB+)
    ) else (
        echo    System memory: %mem_gb%GB - adequate
    )
) else (
    echo    Memory check skipped
)

:: Port conflict resolution
echo.
echo [2/6] Port Conflict Resolution...
netstat -an | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo    Port 8000 in use - attempting to free...
    powershell -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
    timeout /t 3 /nobreak >nul
    netstat -an | findstr ":8000" >nul 2>&1
    if %errorlevel% equ 0 (
        echo    WARNING: Port 8000 still in use (will attempt deployment anyway)
    ) else (
        echo    Port 8000 freed successfully
    )
) else (
    echo    Port 8000 available
)

:: Network connectivity with fallback
echo.
echo [3/6] Network Connectivity Test...
docker pull postgres:15 >nul 2>&1
if %errorlevel% neq 0 (
    echo    WARNING: Cannot download postgres:15 from Docker Hub
    echo    Checking if image exists locally...
    docker image inspect postgres:15 >nul 2>&1
    if %errorlevel% neq 0 (
        echo    ERROR: postgres:15 not available locally or remotely
        echo    Please ensure network connectivity or pre-download image
        pause & exit /b 1
    ) else (
        echo    Using local postgres:15 image
    )
) else (
    echo    postgres:15 image downloaded/verified
)

:: Application image validation with rebuild option
echo.
echo [4/6] Application Image Validation...
docker image inspect agent_monitor-monitor:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo    WARNING: agent_monitor-monitor:latest missing
    if exist "docker\Dockerfile" (
        echo    Attempting to build monitor image...
        docker build -f docker\Dockerfile -t agent_monitor-monitor:latest . >nul 2>&1
        if %errorlevel% neq 0 (
            echo    ERROR: Failed to build monitor image
            pause & exit /b 1
        ) else (
            echo    Monitor image built successfully
        )
    ) else (
        echo    ERROR: Cannot build - docker\Dockerfile missing
        pause & exit /b 1
    )
) else (
    echo    agent_monitor-monitor:latest verified
)

docker image inspect agent_monitor-test-agent:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo    ERROR: agent_monitor-test-agent:latest missing and cannot auto-build
    echo    Please build this image manually
    pause & exit /b 1
) else (
    echo    agent_monitor-test-agent:latest verified
)

:: Enhanced deployment with monitoring
echo.
echo [5/6] Enhanced Production Deployment...
echo    Cleaning previous deployment...
docker-compose -f docker-compose.production.yml down -v >nul 2>&1

echo    Starting deployment with monitoring...
docker-compose -f docker-compose.production.yml up -d
if %errorlevel% neq 0 (
    echo    ERROR: Deployment failed
    echo    Showing recent logs:
    docker-compose -f docker-compose.production.yml logs --tail=20
    pause & exit /b 1
)

:: Enhanced health verification with retry logic
echo.
echo [6/6] Enhanced Health Verification...
echo    Waiting for PostgreSQL startup...
set postgres_ready=0
for /l %%i in (1,1,24) do (
    docker exec agent_monitor-postgres-1 pg_isready -U agent_monitor -d agent_monitor >nul 2>&1
    if not errorlevel 1 (
        set postgres_ready=1
        goto :postgres_verified
    )
    echo    PostgreSQL attempt %%i/24...
    timeout /t 5 /nobreak >nul
)

:postgres_verified
if %postgres_ready% equ 0 (
    echo    ERROR: PostgreSQL failed to start within 2 minutes
    echo    Showing PostgreSQL logs:
    docker logs agent_monitor-postgres-1 --tail=20
    pause & exit /b 1
)

echo    Waiting for Monitor Dashboard...
set monitor_ready=0
for /l %%i in (1,1,18) do (
    powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/agents/' -UseBasicParsing -TimeoutSec 5; exit 0 } catch { exit 1 }" >nul 2>&1
    if not errorlevel 1 (
        set monitor_ready=1
        goto :monitor_verified
    )
    echo    Monitor attempt %%i/18...
    timeout /t 5 /nobreak >nul
)

:monitor_verified
if %monitor_ready% equ 0 (
    echo    ERROR: Monitor Dashboard failed to start within 90 seconds
    echo    Showing Monitor logs:
    docker logs agent_monitor-monitor-dashboard-1 --tail=20
    pause & exit /b 1
)

:: Dashboard update with verification
echo    Updating to latest dashboard...
docker cp web\pulseguard-enterprise-dashboard.html agent_monitor-monitor-dashboard-1:/app/web/ >nul 2>&1
if %errorlevel% equ 0 (
    docker exec agent_monitor-monitor-dashboard-1 ls -la /app/web/pulseguard-enterprise-dashboard.html >nul 2>&1
    if %errorlevel% equ 0 (
        echo    Latest dashboard deployed and verified
    )
)

:: Final system verification
echo.
echo =========================================================
echo              ROBUST DEPLOYMENT COMPLETE
echo =========================================================

for /f %%i in ('docker ps --filter "name=agent_monitor" --filter "status=running" --quiet ^| find /c /v ""') do set RUNNING=%%i

echo.
echo System Status: %RUNNING%/7 containers running
if "%RUNNING%"=="7" (
    echo    SUCCESS: Full production system operational
    echo.
    echo    Production Endpoints:
    echo      Dashboard: http://localhost:8000
    echo      Database:  localhost:5432
    echo      Username:  agent_monitor
    echo      Password:  agent_monitor_password
    echo.
    echo    All health checks passed - system is robust and ready
    start http://localhost:8000/
) else (
    echo    WARNING: Partial deployment detected
    echo    Showing container status:
    docker ps --filter "name=agent_monitor" --format "table {{.Names}}\t{{.Status}}"
    echo.
    echo    Troubleshooting commands:
    echo      docker-compose -f docker-compose.production.yml logs
    echo      docker-compose -f docker-compose.production.yml restart
)

echo.
echo Management:
echo   Status:  docker ps --filter "name=agent_monitor"
echo   Restart: docker-compose -f docker-compose.production.yml restart
echo   Stop:    docker-compose -f docker-compose.production.yml down
echo.
pause