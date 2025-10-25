# PRODUCTION FILES - QUICK REFERENCE
## Exact Files for Consistent Deployment

### ✅ REQUIRED FILES ONLY:
```
docker-compose.production.yml          # Main orchestration
web/pulseguard-enterprise-dashboard.html  # Latest dashboard (188KB)
agent_production_deployment.py         # Agent script
deploy_production_only.bat            # Production deployment
PRODUCTION_FILES.md                   # This manifest
```

### ✅ REQUIRED IMAGES:
```
agent_monitor-monitor:latest           # Monitor container
agent_monitor-test-agent:latest        # Agent container
postgres:15                           # Database (auto-downloaded)
```

### ✅ ONE COMMAND DEPLOYMENT:
```batch
deploy_production_only.bat
```

### ✅ EXPECTED RESULT:
```
7 containers running:
- agent_monitor-postgres-1 (healthy)
- agent_monitor-monitor-dashboard-1 (healthy) 
- agent_monitor-container-agent-1-1 (healthy)
- agent_monitor-container-agent-2-1 (healthy)
- agent_monitor-container-agent-3-1 (healthy)
- agent_monitor-container-agent-4-1 (healthy)
- agent_monitor-container-agent-5-1 (healthy)

Dashboard: http://localhost:8000
```

### 🐘 POSTGRESQL CREDENTIALS:
```
Host: localhost
Port: 5432
Database: agent_monitor
Username: agent_monitor
Password: agent_monitor_password

Connection: postgresql://agent_monitor:agent_monitor_password@localhost:5432/agent_monitor
```

### 🔧 DATABASE COMMANDS:
```bash
# Connect to database:
docker exec -it agent_monitor-postgres-1 psql -U agent_monitor -d agent_monitor

# Check status:
docker exec agent_monitor-postgres-1 pg_isready -U agent_monitor -d agent_monitor
```

### 🚫 IGNORE ALL OTHER FILES:
- Any other docker-compose*.yml files
- Any simple_* scripts  
- Any host-db or no-postgres configurations
- Any development/test files