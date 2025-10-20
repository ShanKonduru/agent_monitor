# PulseGuard™ Production Files Guide

This document clearly identifies all production files and their purposes to avoid confusion.

## 🚀 Main Production Files

### Core Application Files
- **`main_production_server.py`** - Main PulseGuard server application (FastAPI)
- **`main.py`** - Local development server
- **`agent_production_deployment.py`** - Production agent deployment script
- **`example_agent.py`** - Example agent for testing and demonstration
- **`production_agent.py`** - Production-ready agent implementation

### Web Interface Files
- **`web/pulseguard-enterprise-dashboard.html`** - MAIN PulseGuard™ Enterprise Dashboard (159KB React app)
- **`web/basic-agent-monitor-dashboard.html`** - Simple fallback dashboard

### Configuration Files
- **`docker-compose.offline.yml`** - Production Docker Compose (uses host PostgreSQL)
- **`docker-compose.yml`** - Full containerized deployment
- **`Dockerfile.offline`** - Production Docker image
- **`requirements.txt`** - Python dependencies

### Database & API Files
- **`src/database/connection.py`** - Database connection management
- **`src/api/agents.py`** - Agent management API
- **`src/api/health.py`** - Health check API
- **`src/models.py`** - Data models

## 🗑️ Files Removed During Cleanup

### Removed Python Files
- `main_docker.py` ❌ (replaced by main_production_server.py)
- `main_docker_real.py` ❌ (renamed to main_production_server.py)
- `main_v2.py` ❌ (obsolete)
- `main_local.py` ❌ (functionality merged into main.py)
- `simple_container_agent.py` ❌ (renamed to agent_production_deployment.py)
- `demo_agent.py` ❌ (development only)
- `populate_dummy_data.py` ❌ (development only)
- `debug_api.py` ❌ (development only)
- `check_db_values.py` ❌ (development only)

### Removed HTML Files
- `web/dashboard.html` ❌ (renamed to pulseguard-enterprise-dashboard.html)
- `web/dashboard-offline.html` ❌ (renamed to basic-agent-monitor-dashboard.html)
- `web/simple-dashboard.html` ❌ (obsolete)

## 🎯 Quick Start Guide

### For Production Deployment:
```bash
# Start production system
docker-compose -f docker-compose.offline.yml up -d

# Access PulseGuard Dashboard
http://localhost:8000/dashboard
```

### For Local Development:
```bash
# Start local server
python main.py

# Register test agent
python example_agent.py
```

## 📋 File Naming Convention

- **Production files**: Clear, descriptive names indicating purpose
- **Dashboard files**: Include "pulseguard" or "basic" to indicate type
- **Agent files**: Include "production" or "example" to indicate purpose
- **Main files**: Include "production" or indicate environment

## ⚠️ Important Notes

1. **`pulseguard-enterprise-dashboard.html`** is the MAIN dashboard with all features
2. **`basic-agent-monitor-dashboard.html`** is only a fallback
3. **`main_production_server.py`** is the container application
4. **`main.py`** is for local development only

---
*Last Updated: October 19, 2025*
*PulseGuard™ - Intelligent Infrastructure Monitoring Platform*