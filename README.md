# Agent Monitor Framework

A comprehensive monitoring framework for AI/ML agents deployed across multiple Docker containers or local instances, providing real-time performance tracking and dashboard visualization.

## 🚀 Features

- **Multi-Deployment Support**: Monitor agents across Docker, Kubernetes, local instances, and cloud deployments
- **Comprehensive Metrics**: 50+ performance parameters including system resources, business logic, and AI-specific metrics
- **Real-time Dashboard**: Web-based interface with live updates and visualizations
- **Scalable Architecture**: Built with FastAPI, PostgreSQL, InfluxDB, and Redis
- **Agent Client Library**: Easy-to-use Python client for agent integration
- **Health Monitoring**: Automated health checks and alerting system
- **Historical Analysis**: Time-series data storage and trend analysis

## 📋 Architecture

The framework consists of several key components:

- **Monitoring Core Engine**: Collects and processes agent metrics
- **Agent Registry**: Manages agent registration and discovery
- **Data Storage Layer**: PostgreSQL + InfluxDB for configuration and time-series data
- **Communication Layer**: Redis message queuing and HTTP/WebSocket APIs
- **Dashboard**: Real-time web interface for monitoring and alerts

## 🛠 Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- PostgreSQL, Redis, InfluxDB (for local development)

### Quick Start with Docker

1. **Clone and setup:**
   ```bash
   git clone <repository>
   cd agent_monitor
   ```

2. **Start with Docker Compose:**
   ```bash
   # Windows
   007_run_docker.bat
   
   # Linux/Mac
   cd docker && docker-compose up -d
   ```

3. **Access the system:**
   - Monitor API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Grafana Dashboard: http://localhost:3000 (admin/admin)

### Local Development Setup

1. **Initialize environment:**
   ```bash
   000_init.bat    # Initialize git
   001_env.bat     # Create virtual environment
   002_activate.bat # Activate environment
   003_setup.bat   # Install dependencies
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database configurations
   ```

3. **Start the monitoring service:**
   ```bash
   004_run.bat
   ```

4. **Run example agent:**
   ```bash
   006_run_example_agent.bat
   ```

## 🎯 Quick Agent Integration

### Basic Agent Setup

```python
import asyncio
from src.agents.client import AgentMonitorClient, AgentConfig
from src.models import AgentType, DeploymentType

async def main():
    # Configure your agent
    config = AgentConfig(
        monitor_url="http://localhost:8000",
        agent_name="My AI Agent",
        agent_type=AgentType.LLM_AGENT,
        environment="production"
    )
    
    # Create and start monitoring
    async with AgentMonitorClient(config) as client:
        # Your agent logic here
        while True:
            # Simulate work
            await simulate_agent_work()
            
            # Record metrics
            client.record_task_completed(response_time_ms=250)
            
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Agent with Custom Metrics

```python
from src.agents.client import AgentMonitorClient, AgentConfig

# Create client
client = AgentMonitorClient(config)
await client.register()
await client.start_monitoring()

# Register custom metrics
def get_model_accuracy():
    return 0.95  # Your accuracy calculation

def get_token_count():
    return 1500  # Current token count

client.register_custom_metric("model_accuracy", get_model_accuracy)
client.register_custom_metric("token_count", get_token_count)

# Record business events
client.record_task_completed(response_time_ms=150)
client.record_task_failed()
client.set_pending_tasks(5)
```

## 📊 Monitored Parameters

### System Resources
- CPU usage percentage
- Memory usage (bytes & percentage)
- Disk I/O (read/write operations)
- Network I/O (inbound/outbound traffic)
- GPU usage (if applicable)

### Performance Metrics
- Task completion rate
- Average response time
- Throughput (tasks per second)
- Error rate and success rate
- Queue length and pending tasks

### AI/ML Specific Metrics
- Model inference time
- Model accuracy/confidence scores
- Token processing rate (for LLMs)
- Context window utilization
- API call latency

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

## 🔒 Security Features

- JWT-based authentication for agent registration
- API rate limiting and request validation
- Secure communication protocols
- Environment-based configuration management
- Input validation and sanitization

## 📈 Scalability

The framework is designed for horizontal scaling:

- **Load Balancing**: Multiple monitor instances
- **Database Clustering**: PostgreSQL and Redis clustering
- **Data Partitioning**: Time-based and agent-based sharding
- **Caching Strategy**: Multi-level caching with Redis
- **Message Queuing**: Async processing with Celery

## 🛠 Development Tools

### Batch File Commands (Windows)
- `000_init.bat` - Initialize git repository
- `001_env.bat` - Create virtual environment
- `002_activate.bat` - Activate environment
- `003_setup.bat` - Install dependencies
- `004_run.bat` - Start monitoring service
- `005_run_test.bat` - Run test suite
- `005_run_code_cov.bat` - Run with coverage
- `006_run_example_agent.bat` - Start example agent
- `007_run_docker.bat` - Start with Docker
- `008_deactivate.bat` - Deactivate environment

### Project Structure
```
agent_monitor/
├── src/                    # Source code
│   ├── core/              # Core monitoring engine
│   ├── api/               # REST API endpoints
│   ├── agents/            # Agent client library
│   ├── storage/           # Data storage abstractions
│   └── utils/             # Utility functions
├── tests/                 # Test suite
├── docker/                # Docker configurations
├── web/                   # Frontend dashboard (future)
├── docs/                  # Documentation
└── scripts/               # Deployment scripts
```

## 📚 Documentation

- [Architecture Design](ARCHITECTURE.md) - System architecture and design decisions
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Development roadmap and phases
- [Data Models](DATA_MODELS.md) - Complete data schema documentation
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`005_run_test.bat`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

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
