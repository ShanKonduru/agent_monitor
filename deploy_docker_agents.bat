@echo off
:: Docker Desktop Agent Deployment
:: Comprehensive deployment with fallback strategies

echo ========================================
echo  Docker Desktop Agent Deployment
echo ========================================
echo.

:: Create data directory
if not exist "data" mkdir data

echo Testing Docker connectivity...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
) else (
    echo ✅ Docker is running
)

echo.
echo Testing network connectivity...
docker pull hello-world:latest --quiet >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker Hub connectivity works!
    docker rmi hello-world:latest >nul 2>&1
    goto :docker_deployment
) else (
    echo ⚠️  Docker Hub connectivity issues
    goto :local_simulation
)

:docker_deployment
echo.
echo ========================================
echo  Docker Container Deployment
echo ========================================
echo.

echo Building and deploying containers...
docker-compose -f docker-compose.agents.yml up -d --build

if %errorlevel% equ 0 (
    echo ✅ Docker containers deployed successfully!
    goto :show_docker_status
) else (
    echo ❌ Docker deployment failed, using local simulation
    goto :local_simulation
)

:show_docker_status
echo.
echo Docker containers status:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
echo Services:
echo   📊 Dashboard: http://localhost:8000
echo   🐳 Containers: 5 agent containers running
echo.
echo Wait 30 seconds for containers to start...
timeout /t 30 /nobreak >nul
goto :open_dashboard

:local_simulation
echo.
echo ========================================
echo  Local Container Simulation
echo ========================================
echo.

echo Starting monitor server...
start "Monitor Dashboard" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python main.py"

echo Waiting for server to start...
timeout /t 15 /nobreak >nul

echo Starting containerized agents (simulated)...

start "LLM Container 1" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && set AGENT_NAME=🐳 Container LLM Agent 1&& set AGENT_TYPE=llm_agent&& set WORKLOAD_TYPE=llm&& set AGENT_ENVIRONMENT=docker-sim&& python simple_container_agent.py"

start "LLM Container 2" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && set AGENT_NAME=🐳 Container LLM Agent 2&& set AGENT_TYPE=llm_agent&& set WORKLOAD_TYPE=llm&& set AGENT_ENVIRONMENT=docker-sim&& python simple_container_agent.py"

start "API Container" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && set AGENT_NAME=🐳 Container API Agent&& set AGENT_TYPE=api_agent&& set WORKLOAD_TYPE=api&& set AGENT_ENVIRONMENT=docker-sim&& python simple_container_agent.py"

start "Data Container" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && set AGENT_NAME=🐳 Container Data Agent&& set AGENT_TYPE=data_agent&& set WORKLOAD_TYPE=data&& set AGENT_ENVIRONMENT=docker-sim&& python simple_container_agent.py"

start "Monitor Container" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && set AGENT_NAME=🐳 Container Monitor Agent&& set AGENT_TYPE=monitor_agent&& set WORKLOAD_TYPE=standard&& set AGENT_ENVIRONMENT=docker-sim&& python simple_container_agent.py"

echo.
echo ✅ 5 containerized agents started (simulated)
echo Services:
echo   📊 Dashboard: http://localhost:8000
echo   🐳 Agents: 5 simulated containers running
echo.
echo Wait 30 seconds for agents to register...
timeout /t 30 /nobreak >nul

:open_dashboard
echo.
echo ========================================
echo  Deployment Complete!
echo ========================================
echo.
echo Opening dashboard...
start http://localhost:8000/

echo.
echo Your containerized agent monitoring is now running!
echo.
echo To stop:
echo   - Docker: docker-compose -f docker-compose.agents.yml down
echo   - Simulated: Close the terminal windows
echo.
echo Press any key to continue...
pause >nul