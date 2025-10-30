# Agent Monitor - Binary Deployment Package

## Quick Start

### Windows
```cmd
cd scripts
deploy.bat
```

### Linux/Mac
```bash
cd scripts
chmod +x deploy.sh
./deploy.sh
```

## What's Included

- `agent-monitor-dashboard.tar` - Main dashboard Docker image
- `agent-monitor-agents.tar` - Agent Docker image
- `postgres-15.tar` - PostgreSQL database image
- `docker-compose.production.yml` - Production orchestration
- `web/` - Web assets and dashboard UI
- `scripts/` - Deployment automation
- `config/` - Configuration templates
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

## Troubleshooting

### Common Issues
- **Port conflicts**: Change MONITOR_PORT in .env file
- **Docker not found**: Install Docker Desktop
- **Permission denied**: Run as administrator (Windows) or with sudo (Linux)

### Support
See `BINARY_DEPLOYMENT_GUIDE.md` for complete documentation.
