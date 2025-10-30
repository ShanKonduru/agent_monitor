@echo off
echo 🚀 Deploying Agent Monitor - Production
echo ==========================================

:: Check prerequisites
docker --version >nul 2>&1 || (echo ❌ Docker required & pause & exit /b 1)
docker-compose --version >nul 2>&1 || (echo ❌ Docker Compose required & pause & exit /b 1)

:: Navigate to deployment directory
cd /d "%~dp0\.."

:: Load images
echo 📦 Loading Docker images...
docker load -i agent-monitor-dashboard.tar
docker load -i agent-monitor-agents.tar
docker load -i postgres-15.tar

:: Create .env if it doesn't exist
if not exist .env (
    echo 📝 Creating default .env file...
    (
        echo # Database Configuration
        echo DB_PASSWORD=secure_production_password
        echo DB_PORT=5432
        echo.
        echo # Monitor Configuration
        echo MONITOR_PORT=8000
        echo HOST_IP=localhost
        echo.
        echo # Agent Configuration
        echo AGENT_NAME=Production Agent
        echo AGENT_TYPE=LLM_AGENT
        echo WORKLOAD_TYPE=api
    ) > .env
)

:: Deploy stack
echo 🏗️  Starting services...
docker-compose -f docker-compose.production.yml up -d

:: Wait for services
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

:: Health check
echo 🔍 Checking service health...
docker-compose -f docker-compose.production.yml ps

:: Success message
echo 🎉 Deployment complete!
echo 📊 Dashboard: http://localhost:8000
echo 🗃️  Admin: http://localhost:8000/admin
echo 📚 API Docs: http://localhost:8000/docs
pause
