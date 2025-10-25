@echo off
chcp 65001 >nul
:: ON-THE-FLY IMAGE BUILDING DEPLOYMENT
:: Builds images during deployment, handles network issues gracefully

echo =========================================================
echo  ON-THE-FLY IMAGE BUILDING DEPLOYMENT
echo =========================================================
echo.

:: Check if images exist, if not try to build them
echo [1/4] Image Availability Check...

docker image inspect agent_monitor-monitor:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo    agent_monitor-monitor:latest missing - will build during deployment
    set BUILD_NEEDED=1
) else (
    echo    agent_monitor-monitor:latest exists
)

docker image inspect agent_monitor-test-agent:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo    agent_monitor-test-agent:latest missing - will build during deployment
    set BUILD_NEEDED=1
) else (
    echo    agent_monitor-test-agent:latest exists
)

:: Network connectivity test
echo.
echo [2/4] Network Connectivity Test...
docker pull hello-world:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo    WARNING: Network connectivity issues detected
    echo    Will attempt deployment with local images only
    set NETWORK_ISSUES=1
) else (
    echo    Network connectivity OK
    docker rmi hello-world:latest >nul 2>&1
    set NETWORK_ISSUES=0
)

:: Handle PostgreSQL availability
echo.
echo [3/4] PostgreSQL Image Strategy...
if %NETWORK_ISSUES% equ 1 (
    docker image inspect postgres:15 >nul 2>&1
    if %errorlevel% neq 0 (
        echo    ERROR: Network issues prevent PostgreSQL download and no local image exists
        echo    Solutions:
        echo      1. Fix network connectivity
        echo      2. Pre-download postgres:15 image when network is available
        echo      3. Use host PostgreSQL (deploy_production_only.bat with host-db setup)
        pause & exit /b 1
    ) else (
        echo    Using local postgres:15 image
    )
) else (
    echo    Will download postgres:15 if needed
)

:: Deployment with build
echo.
echo [4/4] Deployment with On-The-Fly Building...
echo    Strategy: Build images during docker-compose up

if defined BUILD_NEEDED (
    echo    Building application images...
    if %NETWORK_ISSUES% equ 1 (
        echo    WARNING: Building with network issues - may fail if base images not cached
    )
)

echo    Starting deployment...
docker-compose -f docker-compose.production.yml up -d --build
if %errorlevel% neq 0 (
    echo.
    echo    ERROR: Deployment failed
    echo    This could be due to:
    echo      - Network connectivity issues preventing base image download
    echo      - Missing Dockerfile dependencies
    echo      - Resource constraints
    echo.
    echo    Troubleshooting:
    echo      1. Check network: docker pull python:3.11-slim
    echo      2. Check Dockerfiles exist: docker/Dockerfile, docker/agent.Dockerfile  
    echo      3. Build manually: docker-compose -f docker-compose.production.yml build
    echo      4. View logs: docker-compose -f docker-compose.production.yml logs
    echo.
    pause & exit /b 1
)

:: Verification
echo.
echo    Verifying deployment...
timeout /t 15 /nobreak >nul

for /f %%i in ('docker ps --filter "name=agent_monitor" --filter "status=running" --quiet ^| find /c /v ""') do set RUNNING=%%i

echo.
echo =========================================================
echo         ON-THE-FLY BUILD DEPLOYMENT RESULT
echo =========================================================
echo.

if "%RUNNING%"=="7" (
    echo    SUCCESS: All 7 containers built and running
    echo.
    echo    Images Built On-The-Fly:
    docker images --filter "reference=agent_monitor*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo.
    echo    Production System Ready:
    echo      Dashboard: http://localhost:8000
    echo      Database:  PostgreSQL container
    echo      Agents:    5 production agents
    echo.
    start http://localhost:8000/
) else (
    echo    PARTIAL: %RUNNING%/7 containers running
    echo.
    echo    Container Status:
    docker ps --filter "name=agent_monitor" --format "table {{.Names}}\t{{.Status}}"
    echo.
    echo    Check logs for build/startup issues:
    echo      docker-compose -f docker-compose.production.yml logs --tail=20
)

echo.
echo Management Commands:
echo   View Images: docker images --filter "reference=agent_monitor*"
echo   Rebuild:     docker-compose -f docker-compose.production.yml up -d --build --force-recreate
echo   Logs:        docker-compose -f docker-compose.production.yml logs
echo   Stop:        docker-compose -f docker-compose.production.yml down
echo.
pause