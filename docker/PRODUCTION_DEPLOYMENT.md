# Docker Production Deployment Guide

## Overview

This guide explains how to deploy the Agent Monitor Framework in production using Docker containers. The setup includes a complete monitoring infrastructure with multiple agent types simulating real-world scenarios.

## Architecture

### Production Components

1. **Monitor Service** - Core monitoring API and dashboard
2. **Agent Fleet** - 7 production agents across different types:
   - 2x LLM Agents (GPT-4 style, Claude style)
   - 2x API Agents (Gateway, Auth Service)  
   - 2x Data Agents (ETL Pipeline, Analytics)
   - 1x Monitor Agent (System monitoring)
3. **Infrastructure Services**:
   - PostgreSQL (agent metadata & configuration)
   - Redis (caching & message queuing)
   - InfluxDB (time series metrics)
   - Grafana (advanced dashboards)
   - Nginx (load balancer & reverse proxy)

### Network Architecture

All services run in a dedicated Docker network (`monitor-network`) with:
- Subnet: 172.20.0.0/16
- Internal service discovery via container names
- External access through exposed ports

## Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- 10GB+ disk space

### Development Environment

Start a basic development environment:

```bash
# Windows
cd docker
deploy.bat dev

# Linux/Mac
cd docker
./deploy.sh dev
```

Access points:
- Monitor API: http://localhost:8000
- Dashboard: http://localhost:8000/dashboard
- Grafana: http://localhost:3000 (admin/admin)

### Production Environment

Deploy the full production agent fleet:

```bash
# Windows
cd docker
deploy.bat prod

# Linux/Mac
cd docker
./deploy.sh prod
```

Access points:
- Monitor Dashboard: http://localhost/ (via nginx)
- Grafana: http://localhost/grafana (admin/admin)
- Direct API: http://localhost:8000

## Agent Types & Workloads

### LLM Agents
- **GPT-4 Processing Agent**: Simulates large language model processing
- **Claude Analysis Agent**: Simulates document analysis workflows
- **Metrics**: token_count, model_accuracy, processing_time
- **Characteristics**: Variable processing times, occasional model reloads

### API Agents  
- **REST API Gateway**: High-throughput request processing
- **Auth Service API**: Authentication and authorization service
- **Metrics**: requests_per_minute, cache_hit_ratio, response_time
- **Characteristics**: Fast processing, database integration

### Data Agents
- **ETL Pipeline Agent**: Extract, Transform, Load operations
- **Analytics Engine**: Real-time data analytics
- **Metrics**: records_per_batch, throughput_mbps, processing_time
- **Characteristics**: Batch processing, I/O intensive

### Monitor Agent
- **System Monitor Agent**: Infrastructure monitoring
- **Metrics**: Standard monitoring metrics
- **Characteristics**: Continuous monitoring, health checks

## Deployment Commands

### Basic Operations

```bash
# Start development
deploy.bat dev

# Start production  
deploy.bat prod

# Stop all services
deploy.bat stop

# Clean everything (removes volumes)
deploy.bat clean

# Show status
deploy.bat status
```

### Monitoring & Debugging

```bash
# Show logs for specific service
deploy.bat logs llm-agent-1
deploy.bat logs monitor
deploy.bat logs postgres

# Open dashboard
deploy.bat dashboard

# Check all service status
deploy.bat status
```

## Configuration

### Environment Variables

Agent containers support these environment variables:

- `MONITOR_URL`: Monitor service URL (default: http://monitor:8000)
- `AGENT_NAME`: Display name for the agent
- `AGENT_TYPE`: Type of agent (llm_agent, api_agent, data_agent, monitor_agent)  
- `WORKLOAD_TYPE`: Workload simulation type (llm, api, data, standard)
- `AGENT_VERSION`: Agent version string
- `AGENT_ENVIRONMENT`: Environment name (production, staging, etc.)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

### Custom Agent Deployment

To deploy your own agent:

1. Create agent configuration:
```yaml
custom-agent:
  build:
    context: ..
    dockerfile: docker/agent.Dockerfile
  environment:
    - MONITOR_URL=http://monitor:8000
    - AGENT_NAME=My Custom Agent
    - AGENT_TYPE=api_agent
    - WORKLOAD_TYPE=custom
    - AGENT_VERSION=1.0.0
  command: ["python", "my_agent.py"]
  depends_on:
    - monitor
  networks:
    - monitor-network
```

2. Add to docker-compose-production.yml

3. Redeploy:
```bash
deploy.bat prod
```

## Scaling

### Manual Scaling

Edit `docker-compose-production.yml` and add:

```yaml
deploy:
  replicas: 3  # Scale to 3 instances
```

### Load Testing

The production setup can handle:
- 100+ concurrent agent connections
- 1000+ metrics/second ingestion
- Sub-second dashboard updates
- 24/7 continuous operation

## Monitoring & Observability

### Dashboard Access

1. **Main Dashboard**: http://localhost/
   - Real-time agent status
   - Performance metrics
   - Health monitoring

2. **Grafana**: http://localhost/grafana
   - Advanced analytics
   - Custom dashboards  
   - Historical trends

### Key Metrics

Monitor these production metrics:

- **Agent Health**: Registration status, heartbeat, error rates
- **Performance**: Response times, throughput, resource usage
- **Business**: Task completion rates, custom metrics
- **Infrastructure**: Database connections, memory usage, disk I/O

### Alerting

Set up alerts for:
- Agent disconnections (> 5 minutes)
- High error rates (> 10%)
- Performance degradation (> 2x normal response time)
- Resource exhaustion (> 90% memory/disk)

## Production Considerations

### Security

1. **Network Security**:
   - Use internal Docker networks
   - Expose only necessary ports
   - Implement proper authentication

2. **Secrets Management**:
   - Use Docker secrets for passwords
   - Rotate credentials regularly
   - Monitor access logs

### Performance

1. **Resource Allocation**:
   - Monitor: 2 CPU, 4GB RAM
   - Agents: 0.5 CPU, 1GB RAM each
   - Database: 2 CPU, 4GB RAM
   - InfluxDB: 1 CPU, 2GB RAM

2. **Storage**:
   - PostgreSQL: SSD storage recommended
   - InfluxDB: High I/O disk for metrics
   - Logs: Rotate and archive regularly

### High Availability

1. **Database Backup**:
```bash
# Backup PostgreSQL
docker exec postgres pg_dump -U monitor agent_monitor > backup.sql

# Backup InfluxDB
docker exec influxdb influx backup /tmp/backup
```

2. **Service Health Checks**:
All services include health checks for:
- Automatic restart on failure
- Load balancer integration
- Monitoring alerts

### Troubleshooting

Common issues and solutions:

1. **Agents not registering**:
   - Check network connectivity: `docker network ls`
   - Verify monitor service: `deploy.bat logs monitor`
   - Check agent logs: `deploy.bat logs llm-agent-1`

2. **Performance issues**:
   - Monitor resource usage: `docker stats`
   - Check database connections: `deploy.bat logs postgres`
   - Review InfluxDB metrics: `deploy.bat logs influxdb`

3. **Dashboard not loading**:
   - Verify nginx: `deploy.bat logs nginx`
   - Check monitor service: `deploy.bat status`
   - Test direct API: `curl http://localhost:8000/api/v1/system/status`

## Migration from Development

To migrate from development to production:

1. Export existing data:
```bash
# Export agents
curl http://localhost:8000/api/v1/agents > agents_backup.json
```

2. Stop development environment:
```bash
deploy.bat stop
```

3. Start production environment:
```bash
deploy.bat prod
```

4. Wait for initialization (60+ seconds)

5. Verify deployment:
```bash
deploy.bat status
deploy.bat dashboard
```

## Support & Maintenance

### Log Management

Logs are available via:
```bash
# All services
docker-compose -f docker-compose-production.yml logs

# Specific service
deploy.bat logs monitor

# Follow logs
docker-compose -f docker-compose-production.yml logs -f
```

### Updates & Patches

To update the system:

1. Pull latest code
2. Rebuild images: `docker-compose build`
3. Rolling update: `docker-compose up -d`

### Backup Strategy

Regular backups should include:
- PostgreSQL database (agent metadata)
- InfluxDB data (metrics history)  
- Grafana dashboards (custom configs)
- Agent configurations

For production deployment questions or issues, refer to the main documentation or create an issue in the project repository.