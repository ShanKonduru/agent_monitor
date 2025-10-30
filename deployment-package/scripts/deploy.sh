#!/bin/bash
set -e

echo "🚀 Deploying Agent Monitor - Production"

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose required"; exit 1; }

# Navigate to deployment directory
cd "$^(dirname "$0"^)/.."

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

echo "🎉 Deployment complete!"
echo "📊 Dashboard: http://localhost:${MONITOR_PORT:-8000}"
