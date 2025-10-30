#!/bin/bash
# export_for_deployment.sh - Create binary deployment package

set -e

echo "🚀 Creating Agent Monitor Binary Deployment Package"
echo "=================================================="

# Create deployment directory
DEPLOY_DIR="deployment-package"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR/{scripts,config,secrets}

echo "📦 Step 1: Building production images..."
docker-compose -f docker-compose.production.yml build

echo "💾 Step 2: Exporting Docker images..."
docker save agent_monitor-monitor:latest -o $DEPLOY_DIR/agent-monitor-dashboard.tar
docker save agent_monitor-test-agent:latest -o $DEPLOY_DIR/agent-monitor-agents.tar
docker save postgres:15 -o $DEPLOY_DIR/postgres-15.tar

echo "📋 Step 3: Copying configuration files..."
cp docker-compose.production.yml $DEPLOY_DIR/
cp -r web $DEPLOY_DIR/

echo "🔧 Step 4: Creating deployment scripts..."

# Linux/Mac deployment script
cat > $DEPLOY_DIR/scripts/deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Deploying Agent Monitor - Production"

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose required"; exit 1; }

# Navigate to deployment directory
cd "$(dirname "$0")/.."

# Load images
echo "📦 Loading Docker images..."
docker load -i agent-monitor-dashboard.tar
docker load -i agent-monitor-agents.tar
docker load -i postgres-15.tar

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating default .env file..."
    cat > .env << 'ENVEOF'
# Database Configuration
DB_PASSWORD=secure_production_password
DB_PORT=5432

# Monitor Configuration  
MONITOR_PORT=8000
HOST_IP=localhost

# Agent Configuration
AGENT_NAME=Production Agent
AGENT_TYPE=LLM_AGENT
WORKLOAD_TYPE=api
ENVEOF
fi

# Deploy stack
echo "🏗️  Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 30

# Health check
echo "🔍 Checking service health..."
docker-compose -f docker-compose.production.yml ps

# Test endpoint
if curl -f http://localhost:${MONITOR_PORT:-8000}/api/v1/system/status >/dev/null 2>&1; then
    echo "✅ Dashboard is healthy"
    echo "📊 Dashboard: http://localhost:${MONITOR_PORT:-8000}"
    echo "🗃️  Admin: http://localhost:${MONITOR_PORT:-8000}/admin"
    echo "📚 API Docs: http://localhost:${MONITOR_PORT:-8000}/docs"
else
    echo "❌ Dashboard not responding - check logs:"
    echo "   docker-compose -f docker-compose.production.yml logs monitor-dashboard"
fi

echo "🎉 Deployment complete!"
EOF

# Windows deployment script
cat > $DEPLOY_DIR/scripts/deploy.bat << 'EOF'
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

:: Get port from env
set MONITOR_PORT=8000
for /f "tokens=2 delims==" %%a in ('findstr "MONITOR_PORT" .env 2^>nul') do set MONITOR_PORT=%%a

echo 🎉 Deployment complete!
echo 📊 Dashboard: http://localhost:%MONITOR_PORT%
echo 🗃️  Admin: http://localhost:%MONITOR_PORT%/admin
echo 📚 API Docs: http://localhost:%MONITOR_PORT%/docs
pause
EOF

# Make scripts executable
chmod +x $DEPLOY_DIR/scripts/deploy.sh

echo "🔐 Step 5: Creating security templates..."

# Secure docker-compose template
cat > $DEPLOY_DIR/config/docker-compose.secure.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_DB=agent_monitor
      - POSTGRES_USER=agent_monitor
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - agent-network
    secrets:
      - db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent_monitor -d agent_monitor"]
      interval: 10s
      timeout: 5s
      retries: 5

  monitor-dashboard:
    image: agent_monitor-monitor:latest
    command: python main_production_server.py
    ports:
      - "${MONITOR_PORT:-8000}:8000"
    environment:
      - PYTHONPATH=/app
      - MONITOR_URL=http://${HOST_IP:-localhost}:${MONITOR_PORT:-8000}
      - DATABASE_URL=postgresql+asyncpg://agent_monitor:${DB_PASSWORD}@postgres:5432/agent_monitor
      - SECRET_KEY_FILE=/run/secrets/app_secret
    volumes:
      - agent_data:/app/data
      - ./web:/app/web
    networks:
      - agent-network
      - web-network
    depends_on:
      postgres:
        condition: service_healthy
    secrets:
      - app_secret
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  container-agent:
    image: agent_monitor-test-agent:latest
    command: python agent_production_deployment.py
    restart: unless-stopped
    environment:
      - AGENT_NAME=${AGENT_NAME:-🐳 Container Agent}
      - AGENT_TYPE=${AGENT_TYPE:-LLM_AGENT}
      - WORKLOAD_TYPE=${WORKLOAD_TYPE:-llm}
      - AGENT_ENVIRONMENT=DOCKER
      - MONITOR_URL=http://monitor-dashboard:8000
      - PYTHONPATH=/app
    networks:
      - agent-network
    depends_on:
      monitor-dashboard:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

volumes:
  postgres_data:
  agent_data:

networks:
  agent-network:
    driver: bridge
    internal: true
  web-network:
    driver: bridge

secrets:
  db_password:
    file: ./secrets/db_password.txt
  app_secret:
    file: ./secrets/app_secret.txt
EOF

# Sample secrets
echo "secure_production_password_$(date +%s)" > $DEPLOY_DIR/secrets/db_password.txt
echo "app_secret_key_$(openssl rand -hex 32 2>/dev/null || echo "fallback_secret_$(date +%s)")" > $DEPLOY_DIR/secrets/app_secret.txt

echo "📋 Step 6: Creating documentation..."

# README for deployment package
cat > $DEPLOY_DIR/README.md << 'EOF'
# Agent Monitor - Binary Deployment Package

## Quick Start

### Linux/Mac
```bash
cd scripts
./deploy.sh
```

### Windows
```cmd
cd scripts
deploy.bat
```

## What's Included

- `agent-monitor-dashboard.tar` - Main dashboard Docker image
- `agent-monitor-agents.tar` - Agent Docker image  
- `postgres-15.tar` - PostgreSQL database image
- `docker-compose.production.yml` - Production orchestration
- `web/` - Web assets and dashboard UI
- `scripts/` - Deployment automation
- `config/` - Advanced configuration templates
- `secrets/` - Security templates

## Configuration

Edit `.env` file (created automatically) to customize:
- Database password
- Port mappings  
- Agent configuration
- Host IP address

## Access Points

After deployment:
- **Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin

## Management Commands

```bash
# View logs
docker-compose -f docker-compose.production.yml logs -f

# Scale agents
docker-compose -f docker-compose.production.yml up -d --scale container-agent=5

# Stop services
docker-compose -f docker-compose.production.yml down

# Full cleanup
docker-compose -f docker-compose.production.yml down -v
docker image prune -f
```

## Support

See `BINARY_DEPLOYMENT_GUIDE.md` for complete documentation.
EOF

echo "📊 Step 7: Package summary..."
echo ""
echo "Deployment package created: $DEPLOY_DIR/"
echo "Package contents:"
ls -la $DEPLOY_DIR/
echo ""
echo "Package size:"
du -sh $DEPLOY_DIR/
echo ""
echo "✅ Ready for transfer to target environment!"
echo ""
echo "To deploy on target machine:"
echo "1. Copy entire '$DEPLOY_DIR' folder"
echo "2. Run: cd $DEPLOY_DIR/scripts && ./deploy.sh"
echo "3. Access: http://localhost:8000"