# Agent Monitor - Binary Deployment Guide

## Overview
This guide explains how to deploy the Agent Monitor solution to another environment using **only Docker images (binaries)** - no source code transfer required.

## Prerequisites on Target Machine

### Required Software
```bash
# Docker Engine (Linux/Windows/Mac)
docker --version  # Should be 20.10+ or newer
docker-compose --version  # Should be 1.29+ or newer

# Alternative: Docker Desktop (Windows/Mac)
# Includes both Docker Engine and Docker Compose
```

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Disk**: Minimum 10GB free space
- **Network**: Internet access for initial setup
- **Ports**: 8000, 5432 available (or configurable)

## Deployment Methods

### Method 1: Docker Hub Distribution (Recommended)

#### Step 1: Export Images from Your Development Machine
```powershell
# On your personal laptop - build and export images
cd C:\MyProjects\agent_monitor

# Build production images
docker-compose -f docker-compose.production.yml build

# Export images to tar files
docker save agent_monitor-monitor:latest -o agent-monitor-dashboard.tar
docker save agent_monitor-test-agent:latest -o agent-monitor-agents.tar
docker save postgres:15 -o postgres-15.tar

# Create deployment package
mkdir deployment-package
copy agent-monitor-dashboard.tar deployment-package\
copy agent-monitor-agents.tar deployment-package\
copy postgres-15.tar deployment-package\
copy docker-compose.production.yml deployment-package\
copy web deployment-package\web\ /E
```

#### Step 2: Transfer to Target Machine
```bash
# Copy deployment-package folder to target machine via:
# - USB drive
# - Network share
# - Cloud storage (OneDrive/Google Drive)
# - SCP/SFTP
```

#### Step 3: Deploy on Target Machine
```bash
# On target machine
cd deployment-package

# Load Docker images
docker load -i agent-monitor-dashboard.tar
docker load -i agent-monitor-agents.tar
docker load -i postgres-15.tar

# Verify images loaded
docker images | grep agent_monitor

# Deploy the stack
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps
```

### Method 2: Docker Registry (Enterprise)

#### Step 1: Setup Private Registry (Optional)
```bash
# On target machine or separate server
docker run -d -p 5000:5000 --name registry registry:2

# Or use cloud registries:
# - Docker Hub (public/private)
# - Azure Container Registry
# - AWS ECR
# - Google Container Registry
```

#### Step 2: Push Images from Development
```powershell
# On your development machine
# Tag images for registry
docker tag agent_monitor-monitor:latest localhost:5000/agent-monitor:latest
docker tag agent_monitor-test-agent:latest localhost:5000/agent-agents:latest

# Push to registry
docker push localhost:5000/agent-monitor:latest
docker push localhost:5000/agent-agents:latest
```

#### Step 3: Pull and Deploy on Target
```bash
# On target machine
docker pull localhost:5000/agent-monitor:latest
docker pull localhost:5000/agent-agents:latest

# Update docker-compose.production.yml image references
# Then deploy
docker-compose -f docker-compose.production.yml up -d
```

## Production Configuration Templates

### docker-compose.production.yml (Customizable)
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_DB=agent_monitor
      - POSTGRES_USER=agent_monitor
      - POSTGRES_PASSWORD=${DB_PASSWORD:-agent_monitor_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "${DB_PORT:-5432}:5432"
    networks:
      - agent-network

  monitor-dashboard:
    image: agent_monitor-monitor:latest
    command: python main_production_server.py
    ports:
      - "${MONITOR_PORT:-8000}:8000"
    environment:
      - PYTHONPATH=/app
      - MONITOR_URL=http://${HOST_IP:-localhost}:${MONITOR_PORT:-8000}
      - DATABASE_URL=postgresql+asyncpg://agent_monitor:${DB_PASSWORD:-agent_monitor_password}@postgres:5432/agent_monitor
    volumes:
      - agent_data:/app/data
      - ./web:/app/web  # Mount web assets
    networks:
      - agent-network
    depends_on:
      - postgres

  # Agents can be scaled: docker-compose up --scale container-agent=5
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
      - monitor-dashboard

volumes:
  postgres_data:
  agent_data:

networks:
  agent-network:
    driver: bridge
```

### Environment Configuration (.env)
```env
# Create .env file on target machine
DB_PASSWORD=secure_production_password
DB_PORT=5432
MONITOR_PORT=8000
HOST_IP=your-target-machine-ip

# Agent Configuration
AGENT_NAME=Production Agent
AGENT_TYPE=LLM_AGENT
WORKLOAD_TYPE=api
```

## Deployment Scripts

### deploy.sh (Linux/Mac)
```bash
#!/bin/bash
set -e

echo "🚀 Deploying Agent Monitor - Production"

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose required"; exit 1; }

# Load images if tar files exist
if [ -f "agent-monitor-dashboard.tar" ]; then
    echo "📦 Loading dashboard image..."
    docker load -i agent-monitor-dashboard.tar
fi

if [ -f "agent-monitor-agents.tar" ]; then
    echo "📦 Loading agents image..."
    docker load -i agent-monitor-agents.tar
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

# Test endpoints
if curl -f http://localhost:8000/api/v1/system/status >/dev/null 2>&1; then
    echo "✅ Dashboard is healthy"
else
    echo "❌ Dashboard not responding"
fi

echo "🎉 Deployment complete!"
echo "📊 Dashboard: http://localhost:8000"
echo "🗃️  Admin: http://localhost:8000/admin"
```

### deploy.bat (Windows)
```batch
@echo off
echo 🚀 Deploying Agent Monitor - Production

:: Check prerequisites
docker --version >nul 2>&1 || (echo ❌ Docker required & pause & exit /b 1)
docker-compose --version >nul 2>&1 || (echo ❌ Docker Compose required & pause & exit /b 1)

:: Load images if available
if exist "agent-monitor-dashboard.tar" (
    echo 📦 Loading dashboard image...
    docker load -i agent-monitor-dashboard.tar
)

if exist "agent-monitor-agents.tar" (
    echo 📦 Loading agents image...
    docker load -i agent-monitor-agents.tar
)

:: Deploy stack
echo 🏗️  Starting services...
docker-compose -f docker-compose.production.yml up -d

:: Wait and check
timeout /t 30 /nobreak >nul
echo 🔍 Checking service health...
docker-compose -f docker-compose.production.yml ps

echo 🎉 Deployment complete!
echo 📊 Dashboard: http://localhost:8000
pause
```

## Security Considerations

### Production Hardening
```yaml
# In docker-compose.production.yml
services:
  postgres:
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    # Remove port exposure for internal-only access
    # ports:
    #   - "5432:5432"

  monitor-dashboard:
    environment:
      - SECRET_KEY_FILE=/run/secrets/app_secret
    secrets:
      - app_secret

secrets:
  db_password:
    file: ./secrets/db_password.txt
  app_secret:
    file: ./secrets/app_secret.txt
```

### Network Security
```yaml
networks:
  agent-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
  
  # Separate network for external access
  web-network:
    driver: bridge
```

## Monitoring & Maintenance

### Health Checks
```bash
# Service status
docker-compose -f docker-compose.production.yml ps

# Logs
docker-compose -f docker-compose.production.yml logs -f monitor-dashboard

# Resource usage
docker stats
```

### Backup Strategy
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
docker-compose -f docker-compose.production.yml exec postgres \
    pg_dump -U agent_monitor agent_monitor > backup_${DATE}.sql

# Backup volumes
docker run --rm -v agent_monitor_postgres_data:/data -v $(pwd):/backup \
    ubuntu tar czf /backup/postgres_data_${DATE}.tar.gz /data

# Backup configuration
tar czf config_${DATE}.tar.gz docker-compose.production.yml .env web/
```

### Updates
```bash
# Update images
docker-compose -f docker-compose.production.yml pull

# Rolling update
docker-compose -f docker-compose.production.yml up -d --no-deps monitor-dashboard

# Scale agents
docker-compose -f docker-compose.production.yml up -d --scale container-agent=10
```

## Troubleshooting

### Common Issues
```bash
# Port conflicts
netstat -tulpn | grep 8000
# Change MONITOR_PORT in .env

# Permission issues
sudo chown -R 1000:1000 ./data
sudo chmod -R 755 ./web

# Memory issues
docker system prune -f
docker image prune -f

# Database connection
docker-compose -f docker-compose.production.yml exec postgres \
    psql -U agent_monitor -d agent_monitor -c "SELECT version();"
```

### Performance Tuning
```yaml
services:
  monitor-dashboard:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
  
  postgres:
    command: postgres -c max_connections=200 -c shared_buffers=256MB
```

## Quick Start Checklist

### On Development Machine
- [ ] Build production images: `docker-compose -f docker-compose.production.yml build`
- [ ] Export images: `docker save agent_monitor-monitor:latest -o agent-monitor-dashboard.tar`
- [ ] Copy deployment package to target machine

### On Target Machine
- [ ] Install Docker & Docker Compose
- [ ] Load images: `docker load -i agent-monitor-dashboard.tar`
- [ ] Configure environment: Create `.env` file
- [ ] Deploy: `docker-compose -f docker-compose.production.yml up -d`
- [ ] Verify: Check http://localhost:8000

## Support & Documentation

- **Dashboard**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin
- **Health Check**: http://localhost:8000/api/v1/system/status

This deployment approach ensures:
✅ **No Source Code Exposure** - Only compiled Docker images
✅ **Easy Distribution** - Single deployment package
✅ **Production Ready** - Optimized configuration
✅ **Scalable** - Container-native architecture
✅ **Secure** - Configurable secrets and network isolation