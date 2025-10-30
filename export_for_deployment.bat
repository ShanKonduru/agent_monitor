@echo off
REM export_for_deployment.bat - Create binary deployment package for Windows

echo 🚀 Creating Agent Monitor Binary Deployment Package
echo ==================================================

REM Create deployment directory
set DEPLOY_DIR=deployment-package
if exist %DEPLOY_DIR% rmdir /s /q %DEPLOY_DIR%
mkdir %DEPLOY_DIR%\scripts
mkdir %DEPLOY_DIR%\config
mkdir %DEPLOY_DIR%\secrets

echo 📦 Step 1: Building production images...
docker-compose -f docker-compose.production.yml build

echo 💾 Step 2: Exporting Docker images...
docker save agent_monitor-monitor:latest -o %DEPLOY_DIR%\agent-monitor-dashboard.tar
docker save agent_monitor-test-agent:latest -o %DEPLOY_DIR%\agent-monitor-agents.tar
docker save postgres:15 -o %DEPLOY_DIR%\postgres-15.tar

echo 📋 Step 3: Copying configuration files...
copy docker-compose.production.yml %DEPLOY_DIR%\
xcopy web %DEPLOY_DIR%\web\ /E /I

echo 🔧 Step 4: Creating deployment scripts...

REM Windows deployment script
(
echo @echo off
echo echo 🚀 Deploying Agent Monitor - Production
echo echo ==========================================
echo.
echo :: Check prerequisites
echo docker --version ^>nul 2^>^&1 ^|^| ^(echo ❌ Docker required ^& pause ^& exit /b 1^)
echo docker-compose --version ^>nul 2^>^&1 ^|^| ^(echo ❌ Docker Compose required ^& pause ^& exit /b 1^)
echo.
echo :: Navigate to deployment directory
echo cd /d "%%~dp0\.."
echo.
echo :: Load images
echo echo 📦 Loading Docker images...
echo docker load -i agent-monitor-dashboard.tar
echo docker load -i agent-monitor-agents.tar
echo docker load -i postgres-15.tar
echo.
echo :: Create .env if it doesn't exist
echo if not exist .env ^(
echo     echo 📝 Creating default .env file...
echo     ^(
echo         echo # Database Configuration
echo         echo DB_PASSWORD=secure_production_password
echo         echo DB_PORT=5432
echo         echo.
echo         echo # Monitor Configuration
echo         echo MONITOR_PORT=8000
echo         echo HOST_IP=localhost
echo         echo.
echo         echo # Agent Configuration
echo         echo AGENT_NAME=Production Agent
echo         echo AGENT_TYPE=LLM_AGENT
echo         echo WORKLOAD_TYPE=api
echo     ^) ^> .env
echo ^)
echo.
echo :: Deploy stack
echo echo 🏗️  Starting services...
echo docker-compose -f docker-compose.production.yml up -d
echo.
echo :: Wait for services
echo echo ⏳ Waiting for services to be ready...
echo timeout /t 30 /nobreak ^>nul
echo.
echo :: Health check
echo echo 🔍 Checking service health...
echo docker-compose -f docker-compose.production.yml ps
echo.
echo :: Success message
echo echo 🎉 Deployment complete!
echo echo 📊 Dashboard: http://localhost:8000
echo echo 🗃️  Admin: http://localhost:8000/admin
echo echo 📚 API Docs: http://localhost:8000/docs
echo pause
) > %DEPLOY_DIR%\scripts\deploy.bat

REM Linux deployment script
(
echo #!/bin/bash
echo set -e
echo.
echo echo "🚀 Deploying Agent Monitor - Production"
echo.
echo # Check prerequisites
echo command -v docker ^>/dev/null 2^>^&1 ^|^| { echo "❌ Docker required"; exit 1; }
echo command -v docker-compose ^>/dev/null 2^>^&1 ^|^| { echo "❌ Docker Compose required"; exit 1; }
echo.
echo # Navigate to deployment directory
echo cd "$^(dirname "$0"^)/.."
echo.
echo # Load images
echo echo "📦 Loading Docker images..."
echo docker load -i agent-monitor-dashboard.tar
echo docker load -i agent-monitor-agents.tar
echo docker load -i postgres-15.tar
echo.
echo # Create .env if it doesn't exist
echo if [ ! -f .env ]; then
echo     echo "📝 Creating default .env file..."
echo     cat ^> .env ^<^< 'ENVEOF'
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
echo ENVEOF
echo fi
echo.
echo # Deploy stack
echo echo "🏗️  Starting services..."
echo docker-compose -f docker-compose.production.yml up -d
echo.
echo # Wait for services
echo echo "⏳ Waiting for services to be ready..."
echo sleep 30
echo.
echo # Health check
echo echo "🔍 Checking service health..."
echo docker-compose -f docker-compose.production.yml ps
echo.
echo echo "🎉 Deployment complete!"
echo echo "📊 Dashboard: http://localhost:${MONITOR_PORT:-8000}"
) > %DEPLOY_DIR%\scripts\deploy.sh

echo 🔐 Step 5: Creating security templates...

REM Sample environment file
(
echo # Agent Monitor Production Configuration
echo.
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
echo.
echo # Security ^(Optional^)
echo # Enable for secret file-based authentication
echo # USE_SECRETS=true
) > %DEPLOY_DIR%\config\.env.template

REM Sample secrets
echo secure_production_password_%RANDOM% > %DEPLOY_DIR%\secrets\db_password.txt
echo app_secret_key_%RANDOM%_%RANDOM% > %DEPLOY_DIR%\secrets\app_secret.txt

echo 📋 Step 6: Creating documentation...

REM README for deployment package
(
echo # Agent Monitor - Binary Deployment Package
echo.
echo ## Quick Start
echo.
echo ### Windows
echo ```cmd
echo cd scripts
echo deploy.bat
echo ```
echo.
echo ### Linux/Mac
echo ```bash
echo cd scripts
echo chmod +x deploy.sh
echo ./deploy.sh
echo ```
echo.
echo ## What's Included
echo.
echo - `agent-monitor-dashboard.tar` - Main dashboard Docker image
echo - `agent-monitor-agents.tar` - Agent Docker image
echo - `postgres-15.tar` - PostgreSQL database image
echo - `docker-compose.production.yml` - Production orchestration
echo - `web/` - Web assets and dashboard UI
echo - `scripts/` - Deployment automation
echo - `config/` - Configuration templates
echo - `secrets/` - Security templates
echo.
echo ## Configuration
echo.
echo Edit `.env` file ^(created automatically^) to customize:
echo - Database password
echo - Port mappings
echo - Agent configuration
echo - Host IP address
echo.
echo ## Access Points
echo.
echo After deployment:
echo - **Dashboard**: http://localhost:8000
echo - **API Documentation**: http://localhost:8000/docs
echo - **Admin Panel**: http://localhost:8000/admin
echo.
echo ## Management Commands
echo.
echo ```bash
echo # View logs
echo docker-compose -f docker-compose.production.yml logs -f
echo.
echo # Scale agents
echo docker-compose -f docker-compose.production.yml up -d --scale container-agent=5
echo.
echo # Stop services
echo docker-compose -f docker-compose.production.yml down
echo.
echo # Full cleanup
echo docker-compose -f docker-compose.production.yml down -v
echo docker image prune -f
echo ```
echo.
echo ## Troubleshooting
echo.
echo ### Common Issues
echo - **Port conflicts**: Change MONITOR_PORT in .env file
echo - **Docker not found**: Install Docker Desktop
echo - **Permission denied**: Run as administrator ^(Windows^) or with sudo ^(Linux^)
echo.
echo ### Support
echo See `BINARY_DEPLOYMENT_GUIDE.md` for complete documentation.
) > %DEPLOY_DIR%\README.md

echo 📊 Step 7: Package summary...
echo.
echo Deployment package created: %DEPLOY_DIR%\
echo Package contents:
dir %DEPLOY_DIR%
echo.
echo ✅ Ready for transfer to target environment!
echo.
echo To deploy on target machine:
echo 1. Copy entire '%DEPLOY_DIR%' folder
echo 2. Run: cd %DEPLOY_DIR%\scripts ^&^& deploy.bat
echo 3. Access: http://localhost:8000
echo.
pause