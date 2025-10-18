@echo off
:: Multi-Agent Container Simulation Demo
:: This demonstrates what containerized agents would look like

echo ================================
echo  Multi-Agent Container Demo
echo ================================
echo.

:: Start the monitoring server in the background
echo Starting monitoring server...
start "Monitor Server" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python main.py"

:: Wait for server to start
echo Waiting for server to initialize...
timeout /t 10 /nobreak >nul

:: Start multiple agents simulating different containers
echo.
echo Starting containerized agents...

:: LLM Agent Container 1
start "LLM Agent 1" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && set AGENT_NAME=Container LLM Agent 1&& set AGENT_TYPE=llm_agent&& set WORKLOAD_TYPE=llm&& set AGENT_ENVIRONMENT=container-1&& python simple_container_agent.py"

:: LLM Agent Container 2  
start "LLM Agent 2" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && set AGENT_NAME=Container LLM Agent 2&& set AGENT_TYPE=llm_agent&& set WORKLOAD_TYPE=llm&& set AGENT_ENVIRONMENT=container-2&& python simple_container_agent.py"

:: API Agent Container
start "API Agent" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && set AGENT_NAME=Container API Agent&& set AGENT_TYPE=api_agent&& set WORKLOAD_TYPE=api&& set AGENT_ENVIRONMENT=container-3&& python simple_container_agent.py"

:: Data Agent Container
start "Data Agent" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && set AGENT_NAME=Container Data Agent&& set AGENT_TYPE=data_agent&& set WORKLOAD_TYPE=data&& set AGENT_ENVIRONMENT=container-4&& python simple_container_agent.py"

:: Monitor Agent Container
start "Monitor Agent" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && set AGENT_NAME=Container Monitor Agent&& set AGENT_TYPE=monitor_agent&& set WORKLOAD_TYPE=standard&& set AGENT_ENVIRONMENT=container-5&& python simple_container_agent.py"

echo.
echo ========================================
echo  Container Demo Started!
echo ========================================
echo.
echo Services running:
echo   - Monitor Server: http://localhost:8000
echo   - 5 Containerized Agents (simulated)
echo.
echo Wait 30 seconds, then check:
echo   - Dashboard: http://localhost:8000/
echo   - API: http://localhost:8000/api/v1/agents
echo.
echo Press any key to open dashboard...
pause >nul
start http://localhost:8000/

echo.
echo Demo is running! Close the terminal windows to stop.