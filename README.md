# 🐳 Agent Monitor Framework - Containerized Edition

A production-ready containerized monitoring framework for AI/ML agents with unified database architecture, real-time dashboard, and Docker deployment capabilities.

## 🎉 **Currently Running**

✅ **5 Containerized Agents** actively processing workloads  
✅ **Unified Database** with persistent storage  
✅ **Real-time Dashboard** at http://localhost:8000  
✅ **Docker Production Deployment** with health monitoring  
✅ **Agent Registry** with automatic discovery  

## 🚀 Features

### 🐳 **Container-First Architecture**
- **Docker Production Deployment**: Full containerized stack with Docker Compose
- **Container Health Monitoring**: Real-time container status and resource tracking
- **Network Isolation**: Secure inter-container communication via Docker networks
- **Persistent Storage**: Unified database with Docker volume mounting
- **Auto-Restart Policies**: Resilient container management with automatic recovery

### 🗄️ **Unified Database System**
- **PostgreSQL Production**: Scalable PostgreSQL database with persistent storage
- **Unified Architecture**: All agent data centralized in production-grade database
- **Data Persistence**: Agent registrations and metrics survive container restarts
- **High Availability**: Connection pooling and health checks for reliability
- **Backup Ready**: Volume-based backup and recovery system

### � **Real-time Monitoring**
- **Live Agent Dashboard**: 5 containerized agents with real-time status updates
- **Workload Processing**: LLM, API, Data, Monitor, and ML agent types
- **Health Checks**: Container-level and application-level health monitoring
- **Performance Metrics**: Resource usage, task completion, and response times
- **Registration Tracking**: Automatic agent discovery and registration status

### 🤖 **Multi-Agent Support**
- **LLM Agent**: Language model processing with simulated workloads
- **API Agent**: RESTful API request handling and response management
- **Data Agent**: Data processing and analysis task execution
- **Monitor Agent**: System monitoring and health check operations
- **ML Agent**: Machine learning model inference and training tasks

## 📋 Current Architecture

### 🐳 **Containerized Deployment**
```
🌐 Docker Desktop
├── 🖥️  Monitor Dashboard (Port 8000)
├── 🤖 Container Agent 1 (LLM)
├── 🔌 Container Agent 2 (API) 
├── 📊 Container Agent 3 (Data)
├── 📈 Container Agent 4 (Monitor)
├── 🧠 Container Agent 5 (ML)
├── � PostgreSQL Database (Production)
└── 🌐 agent_monitor_agent-network
```

### 🗄️ **Database Architecture**
- **Production**: PostgreSQL 15 with persistent Docker volume (`postgres_data`)
- **Location**: Dedicated PostgreSQL container with health checks
- **Connection**: `postgresql://monitor_user:secure_monitor_pass@postgres:5432/agent_monitor`
- **Connection**: `sqlite+aiosqlite:///./data/agent_monitor.db`

📖 **[Unified Database Architecture Guide](./docs/UNIFIED_DATABASE_ARCHITECTURE.md)**

## � Quick Start

### 🐳 **Docker Production Deployment (Recommended)**

**Prerequisites:** Docker Desktop installed and running

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ShanKonduru/agent_monitor
   cd agent_monitor
   ```

2. **Deploy containerized system:**
   ```bash
   # Start production deployment with 5 containerized agents
   .\start_docker_production.bat
   
   # Or manually with Docker Compose
   docker-compose -f docker-compose.production.yml up -d
   ```

3. **Access your system:**
   - 📊 **Dashboard**: http://localhost:8000
   - 📋 **API Docs**: http://localhost:8000/docs  
   - 🤖 **Agent Status**: http://localhost:8000/api/v1/agents/
   - 🗄️ **Database**: Persistent Docker volume storage

### 🗄️ **Database Configuration**

#### **PostgreSQL Production Database** ✅
```bash
# Production database with persistent storage
# Data persists in Docker volume: postgres_data
docker volume inspect postgres_data

# Database health check
docker exec agent_monitor_postgres pg_isready -U monitor_user -d agent_monitor
```

#### **Database Management**
```bash
# View database logs
docker logs agent_monitor_postgres

# Manual database deployment
docker-compose -f docker-compose.production.yml up postgres -d
```

### 💻 **Local Development Setup**

1. **Initialize environment:**
   ```bash
   000_init.bat    # Initialize git repository
   001_env.bat     # Create virtual environment  
   002_activate.bat # Activate Python environment
   003_setup.bat   # Install all dependencies
   ```

2. **Start local development:**
   ```bash
   004_run.bat     # Start monitor server + dashboard + agents
   ```

3. **Run individual components:**
   ```bash
   # Monitor server only
   python main.py
   
   # Example agents
   006_run_example_agent.bat
   
   # Test suite
   005_run_test.bat
   ```

## 🎯 Container Management

### **Current Deployment Status**

```bash
# Check running containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# View container logs
docker-compose -f docker-compose.production.yml logs

# Restart specific agent
docker restart agent_monitor-container-agent-1-1

# Scale agents (add more containers)
docker-compose -f docker-compose.production.yml up -d --scale container-agent-1=3
```

### **Database Management**

```bash
# Check database volume
docker volume inspect agent_monitor_agent_data

# Backup database
docker run --rm -v agent_monitor_agent_data:/data -v ./backup:/backup alpine cp /data/agent_monitor.db /backup/

# View database inside container
docker exec agent_monitor-monitor-dashboard-1 ls -la /app/data/

# Database health check
curl http://localhost:8000/api/v1/agents/
```

### **Agent Integration Example**

```python
import asyncio
from src.agents.client import AgentMonitorClient, AgentConfig
from src.models import AgentType, DeploymentType

async def main():
    # Configure containerized agent
    config = AgentConfig(
        monitor_url="http://monitor-dashboard:8000",  # Docker network URL
        agent_name="My Containerized Agent",
        agent_type=AgentType.LLM_AGENT,
        deployment_type=DeploymentType.DOCKER,
        environment="production"
    )
    
    # Create and start monitoring
    async with AgentMonitorClient(config) as client:
        while True:
            # Simulate containerized workload
            await process_container_task()
            
            # Record metrics to unified database
            client.record_task_completed(response_time_ms=250)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 Monitored Agent Types & Metrics

### 🤖 **Currently Running Agents**

| Agent Type | Container | Workload | Status |
|------------|-----------|----------|---------|
| 🧠 **LLM Agent** | `container-agent-1` | Language model processing | ✅ Active |
| 🔌 **API Agent** | `container-agent-2` | REST API request handling | ✅ Active |
| 📊 **Data Agent** | `container-agent-3` | Data analysis & processing | ✅ Active |
| 📈 **Monitor Agent** | `container-agent-4` | System health monitoring | ✅ Active |
| 🧠 **ML Agent** | `container-agent-5` | Machine learning inference | ✅ Active |

### � **Container Metrics**
- **Container Health**: CPU, memory, network usage per container
- **Registration Status**: Agent discovery and connection tracking
- **Workload Processing**: Task completion rates by agent type
- **Network Communication**: Inter-container API call latency
- **Database Operations**: Unified database read/write performance

### 🔧 **Performance Monitoring**
- **Response Times**: Real-time API response measurements
- **Task Throughput**: Completed tasks per second by agent
- **Error Tracking**: Failed registrations and processing errors
- **Resource Usage**: Container resource consumption patterns
- **Health Checks**: Automated container and application health verification

### 🗄️ **Database Metrics**
- **Connection Pool**: Database connection utilization
- **Query Performance**: SQL query execution times
- **Storage Usage**: Database file size and growth tracking
- **Data Persistence**: Volume mount and backup status
- **Migration Readiness**: PostgreSQL transition monitoring

### Health & Status
- Agent availability and uptime
- Heartbeat monitoring
- Health check results
- Alert generation and management

## 🔧 API Endpoints

### Agent Management
- `POST /api/v1/agents/register` - Register new agent
- `GET /api/v1/agents` - List all agents
- `GET /api/v1/agents/{id}` - Get agent details
- `POST /api/v1/agents/{id}/heartbeat` - Send heartbeat
- `POST /api/v1/agents/{id}/metrics` - Submit metrics

### Metrics & Analytics
- `GET /api/v1/metrics` - Query historical metrics
- `GET /api/v1/metrics/dashboard/data` - Dashboard data
- `GET /api/v1/metrics/system/summary` - System overview

### Health Monitoring
- `GET /api/v1/health/{id}` - Agent health status
- `GET /api/v1/health/alerts/active` - Active alerts
- `POST /api/v1/health/{id}/check` - Trigger health check

## 🧪 Testing

### Run Test Suite
```bash
# All tests
005_run_test.bat

# With coverage
005_run_code_cov.bat

# Specific test categories
pytest -m unit        # Unit tests
pytest -m integration # Integration tests
pytest -m performance # Performance tests
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component functionality
- **Performance Tests**: High-volume and scalability testing
- **Edge Case Tests**: Boundary condition testing

## 🔒 Container Security

### **Network Isolation**
- **Docker Networks**: Isolated `agent_monitor_agent-network` for secure communication
- **Port Exposure**: Only dashboard port (8000) exposed to host
- **Internal Communication**: Container-to-container via Docker DNS
- **No External Access**: Database and agent containers isolated from external network

### **Data Security**
- **Volume Encryption**: Docker volumes with optional encryption
- **Environment Variables**: Secure configuration management via Docker secrets
- **Non-Root Users**: Containers run with dedicated `agent` user (non-root)
- **Read-Only Filesystems**: Application files mounted read-only where possible

## 📈 Container Scalability

### **Horizontal Scaling**
```bash
# Scale specific agent types
docker-compose -f docker-compose.production.yml up -d --scale container-agent-1=3

# Add new agent types
docker-compose -f docker-compose.production.yml up -d new-agent-type

# Load balancing with nginx (future enhancement)
docker-compose -f docker-compose.production.yml -f docker-compose.loadbalancer.yml up -d
```

### **Resource Management**
- **Container Limits**: CPU and memory limits per container
- **Health Checks**: Automatic container restart on failure
- **Volume Management**: Persistent storage with backup capabilities
- **Database Scaling**: Ready for PostgreSQL clustering when needed

## 🛠 Development Tools

## 🛠 Management Commands

### **Container Operations**
```bash
# View all running containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Stop all containers
docker-compose -f docker-compose.production.yml down

# Restart with latest changes
docker-compose -f docker-compose.production.yml up -d --build

# View real-time logs
docker-compose -f docker-compose.production.yml logs -f
```

### **Development Scripts (Windows)**
- `start_docker_production.bat` - Deploy production containers
- `deploy_postgresql.bat` - Deploy with PostgreSQL database  
- `000_init.bat` - Initialize git repository
- `001_env.bat` - Create virtual environment
- `002_activate.bat` - Activate environment
- `003_setup.bat` - Install dependencies
- `004_run.bat` - Start local development
- `005_run_test.bat` - Run test suite
- `006_run_example_agent.bat` - Start example agent

## 📁 Container Architecture

```text
🐳 Docker Desktop
├── 📊 agent_monitor-monitor-dashboard-1    (Port 8000)
├── 🤖 agent_monitor-container-agent-1-1    (LLM Agent)
├── 🔌 agent_monitor-container-agent-2-1    (API Agent)
├── 📊 agent_monitor-container-agent-3-1    (Data Agent)
├── 📈 agent_monitor-container-agent-4-1    (Monitor Agent)
├── 🧠 agent_monitor-container-agent-5-1    (ML Agent)
├── 🗄️ agent_monitor_agent_data            (Database Volume)
└── 🌐 agent_monitor_agent-network         (Docker Network)
```

## 📚 Documentation

### **Container & Database Guides**
- 📖 [Unified Database Architecture](./docs/UNIFIED_DATABASE_ARCHITECTURE.md) - Complete database setup and management
- 🐳 [Docker Deployment Guide](./docs/DOCKER_BUILD_STATUS.md) - Container deployment status and troubleshooting
- 🏗️ [System Architecture](./docs/SYSTEM_ARCHITECTURE.md) - Overall system design and components

### **Development Resources**
- 📋 [Implementation Plan](./docs/IMPLEMENTATION_PLAN.md) - Development roadmap and phases
- 📊 [Data Models](./docs/DATA_MODELS.md) - Database schema and models
- 🔧 [API Documentation](http://localhost:8000/docs) - Interactive API documentation (when running)
- 📈 [Metrics Guide](./docs/METRICS_IMPLEMENTATION_GUIDE.md) - Monitoring and metrics implementation

## 🎯 **Current Status**

✅ **Production Ready**: 5 containerized agents running in Docker Desktop  
✅ **PostgreSQL Database**: Production-grade database with persistent storage  
✅ **Real-time Dashboard**: Live monitoring at http://localhost:8000  
✅ **Agent Registry**: Automatic agent discovery and registration  
✅ **Health Monitoring**: Container and application health checks  
✅ **Scalable Architecture**: Enterprise-ready database and container orchestration  

## 🚀 **Quick Access**

- **🖥️ Dashboard**: http://localhost:8000
- **📋 API Docs**: http://localhost:8000/docs  
- **🤖 Agent Status**: http://localhost:8000/api/v1/agents/
- **📊 Metrics**: Real-time performance data
- **🗄️ Database**: Persistent Docker volume storage

## 🤝 Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Test with containers: `docker-compose -f docker-compose.production.yml up -d`
4. Run the test suite: `005_run_test.bat`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 **Ready to Monitor Your Agents!**

Your containerized Agent Monitor Framework is deployed and ready for production use. Access the dashboard at **http://localhost:8000** to see your 5 active agents in real-time!

## 🆘 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Comprehensive docs in the `/docs` folder
- **Examples**: See `example_agent.py` for implementation examples
- **API Reference**: Available at `/docs` endpoint when running

## 🔮 Roadmap

- [ ] Web-based dashboard frontend
- [ ] Kubernetes operator for automated deployment
- [ ] Machine learning-based anomaly detection
- [ ] Multi-tenant support
- [ ] Advanced alerting and notification system
- [ ] Agent performance prediction and optimization
- [ ] Integration with popular ML frameworks (TensorFlow, PyTorch)
- [ ] Custom plugin architecture for extensibility

[Specify the project license, if any.]
