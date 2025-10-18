@echo off
:: Production Docker Deployment - Using built agent-monitor image
echo ========================================
echo  Production Container Deployment
echo ========================================
echo.

echo Checking Docker and agent-monitor image...
docker images agent-monitor:latest
if %errorlevel% neq 0 (
    echo ❌ agent-monitor:latest image not found
    echo Please build the image first: docker build -f docker/agent.Dockerfile -t agent-monitor:latest .
    pause
    exit /b 1
) else (
    echo ✅ agent-monitor:latest image found
)

echo.
echo Deploying production containers...
docker-compose -f docker-compose.production.yml up -d

if %errorlevel% equ 0 (
    echo ✅ Production containers deployed successfully!
    echo.
    echo Waiting for services to start...
    timeout /t 45 /nobreak >nul
    
    echo.
    echo Container status:
    docker-compose -f docker-compose.production.yml ps
    
    echo.
    echo ========================================
    echo  🐳 CONTAINERIZED AGENT MONITORING 🐳
    echo ========================================
    echo.
    echo Services Running:
    echo   📊 Monitor Dashboard: http://localhost:8000
    echo   🤖 Container Agents: 5 production agents
    echo   🔗 Network: Isolated agent-network
    echo.
    echo Opening dashboard...
    start http://localhost:8000/
    
    echo.
    echo ========================================
    echo  Deployment Complete!
    echo ========================================
    echo.
    echo Your containerized agent monitoring system is now running!
    echo.
    echo Commands:
    echo   Stop:     docker-compose -f docker-compose.production.yml down
    echo   Logs:     docker-compose -f docker-compose.production.yml logs
    echo   Status:   docker-compose -f docker-compose.production.yml ps
    echo   Restart:  docker-compose -f docker-compose.production.yml restart
    echo.
) else (
    echo ❌ Deployment failed
    echo Check the logs: docker-compose -f docker-compose.production.yml logs
)

pause