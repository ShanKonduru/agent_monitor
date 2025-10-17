# Agent Monitor Framework - Data Models & Schemas

## Core Data Models

### 1. Agent Information Models

```python
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class AgentType(str, Enum):
    """Types of agents that can be monitored"""
    LLM_AGENT = "llm_agent"
    ML_MODEL = "ml_model"
    CHATBOT = "chatbot"
    API_AGENT = "api_agent"
    WORKFLOW_AGENT = "workflow_agent"
    CUSTOM = "custom"

class AgentStatus(str, Enum):
    """Current status of an agent"""
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

class DeploymentType(str, Enum):
    """Where the agent is deployed"""
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    LOCAL = "local"
    CLOUD = "cloud"
    SERVERLESS = "serverless"

class AgentInfo(BaseModel):
    """Complete agent information"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., description="Human-readable agent name")
    type: AgentType = Field(..., description="Type of agent")
    version: str = Field(..., description="Agent version")
    description: Optional[str] = Field(None, description="Agent description")
    
    # Deployment Information
    deployment_type: DeploymentType = Field(..., description="Deployment environment")
    host: str = Field(..., description="Host machine or container ID")
    port: Optional[int] = Field(None, description="Port if applicable")
    environment: str = Field(..., description="Environment (dev/staging/prod)")
    
    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent configuration")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    # Registration Info
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    status: AgentStatus = Field(default=AgentStatus.UNKNOWN)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class AgentSummary(BaseModel):
    """Lightweight agent summary for lists"""
    id: str
    name: str
    type: AgentType
    status: AgentStatus
    last_seen: datetime
    environment: str
    health_score: float = Field(..., ge=0.0, le=1.0, description="Overall health score")
```

### 2. Metrics Models

```python
class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class ResourceMetrics(BaseModel):
    """System resource utilization metrics"""
    cpu_usage_percent: float = Field(..., ge=0.0, le=100.0)
    memory_usage_bytes: int = Field(..., ge=0)
    memory_usage_percent: float = Field(..., ge=0.0, le=100.0)
    disk_usage_bytes: int = Field(..., ge=0)
    disk_io_read_bytes: int = Field(default=0, ge=0)
    disk_io_write_bytes: int = Field(default=0, ge=0)
    network_io_rx_bytes: int = Field(default=0, ge=0)
    network_io_tx_bytes: int = Field(default=0, ge=0)
    gpu_usage_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    gpu_memory_usage_bytes: Optional[int] = Field(None, ge=0)

class PerformanceMetrics(BaseModel):
    """Performance and business logic metrics"""
    tasks_completed: int = Field(default=0, ge=0)
    tasks_failed: int = Field(default=0, ge=0)
    tasks_pending: int = Field(default=0, ge=0)
    average_response_time_ms: float = Field(default=0.0, ge=0.0)
    throughput_per_second: float = Field(default=0.0, ge=0.0)
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    uptime_seconds: int = Field(default=0, ge=0)

class AIMetrics(BaseModel):
    """AI/ML specific metrics"""
    model_inference_time_ms: Optional[float] = Field(None, ge=0.0)
    model_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    tokens_processed: Optional[int] = Field(None, ge=0)
    tokens_per_second: Optional[float] = Field(None, ge=0.0)
    context_length: Optional[int] = Field(None, ge=0)
    api_calls_made: Optional[int] = Field(None, ge=0)
    api_call_latency_ms: Optional[float] = Field(None, ge=0.0)

class AgentMetrics(BaseModel):
    """Complete metrics payload from an agent"""
    agent_id: str = Field(..., description="Agent identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Core metrics
    resource_metrics: ResourceMetrics
    performance_metrics: PerformanceMetrics
    ai_metrics: Optional[AIMetrics] = None
    
    # Custom metrics
    custom_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # Health indicators
    health_checks: Dict[str, bool] = Field(default_factory=dict)
    alerts: List[str] = Field(default_factory=list)

class MetricsQuery(BaseModel):
    """Query parameters for retrieving metrics"""
    agent_ids: Optional[List[str]] = Field(None, description="Filter by agent IDs")
    start_time: datetime = Field(..., description="Start time for query")
    end_time: datetime = Field(..., description="End time for query")
    metric_names: Optional[List[str]] = Field(None, description="Specific metrics to retrieve")
    aggregation: Optional[str] = Field(None, description="Aggregation method (avg, sum, max, min)")
    interval: Optional[str] = Field(None, description="Time interval for aggregation")
```

### 3. Health & Status Models

```python
class HealthCheck(BaseModel):
    """Individual health check result"""
    name: str = Field(..., description="Name of the health check")
    status: bool = Field(..., description="Health check result")
    message: Optional[str] = Field(None, description="Additional information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time_ms: float = Field(..., ge=0.0, description="Time taken for check")

class HealthStatus(BaseModel):
    """Overall health status of an agent"""
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    overall_status: AgentStatus
    health_score: float = Field(..., ge=0.0, le=1.0, description="Calculated health score")
    
    # Individual checks
    checks: List[HealthCheck] = Field(default_factory=list)
    
    # System vitals
    is_responsive: bool = Field(..., description="Is the agent responding to requests")
    last_heartbeat: datetime = Field(..., description="Last heartbeat received")
    uptime_seconds: int = Field(..., ge=0, description="Current uptime")

class Alert(BaseModel):
    """Alert/notification model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    severity: str = Field(..., description="critical, warning, info")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Detailed alert message")
    metric_name: Optional[str] = Field(None, description="Related metric")
    threshold: Optional[float] = Field(None, description="Threshold that was breached")
    current_value: Optional[float] = Field(None, description="Current metric value")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(None)
    is_active: bool = Field(default=True)
```

### 4. Configuration Models

```python
class MonitoringConfig(BaseModel):
    """Monitoring configuration for an agent"""
    agent_id: str
    
    # Collection settings
    metrics_interval_seconds: int = Field(default=60, ge=1, le=3600)
    health_check_interval_seconds: int = Field(default=30, ge=5, le=300)
    enable_resource_monitoring: bool = Field(default=True)
    enable_performance_monitoring: bool = Field(default=True)
    enable_ai_monitoring: bool = Field(default=False)
    
    # Thresholds for alerts
    cpu_threshold: float = Field(default=80.0, ge=0.0, le=100.0)
    memory_threshold: float = Field(default=85.0, ge=0.0, le=100.0)
    error_rate_threshold: float = Field(default=0.05, ge=0.0, le=1.0)
    response_time_threshold_ms: float = Field(default=5000.0, ge=0.0)
    
    # Custom thresholds
    custom_thresholds: Dict[str, float] = Field(default_factory=dict)
    
    # Data retention
    metrics_retention_days: int = Field(default=30, ge=1, le=365)
    logs_retention_days: int = Field(default=7, ge=1, le=90)

class DashboardConfig(BaseModel):
    """Dashboard configuration"""
    refresh_interval_seconds: int = Field(default=30, ge=5, le=300)
    default_time_range_hours: int = Field(default=24, ge=1, le=168)
    max_agents_per_page: int = Field(default=50, ge=10, le=200)
    enable_real_time_updates: bool = Field(default=True)
    chart_types: List[str] = Field(default_factory=lambda: ["line", "bar", "gauge"])
```

### 5. API Response Models

```python
class RegisterResponse(BaseModel):
    """Response after agent registration"""
    agent_id: str
    status: str
    message: str
    monitoring_endpoints: Dict[str, str]
    config: MonitoringConfig

class MetricsResponse(BaseModel):
    """Response for metrics queries"""
    query: MetricsQuery
    total_points: int
    agents: List[str]
    time_range: Dict[str, datetime]
    data: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    """Response for health status"""
    agent_id: str
    status: AgentStatus
    health_score: float
    last_updated: datetime
    checks: List[HealthCheck]
    recent_alerts: List[Alert]

class DashboardData(BaseModel):
    """Complete dashboard data"""
    summary: Dict[str, Any]
    agents: List[AgentSummary]
    system_metrics: Dict[str, Any]
    active_alerts: List[Alert]
    performance_trends: Dict[str, List[Dict[str, Any]]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### 6. Event Models

```python
class EventType(str, Enum):
    """Types of events in the system"""
    AGENT_REGISTERED = "agent_registered"
    AGENT_DEREGISTERED = "agent_deregistered"
    AGENT_STATUS_CHANGED = "agent_status_changed"
    METRIC_THRESHOLD_EXCEEDED = "metric_threshold_exceeded"
    HEALTH_CHECK_FAILED = "health_check_failed"
    SYSTEM_ERROR = "system_error"

class SystemEvent(BaseModel):
    """System event model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EventType
    agent_id: Optional[str] = Field(None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)
    severity: str = Field(default="info")  # info, warning, error, critical
    message: str
    source: str = Field(default="monitor_system")
```

## Database Schema Definitions

### PostgreSQL Tables (Configuration & Metadata)

```sql
-- Agents table
CREATE TABLE agents (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    version VARCHAR(100) NOT NULL,
    description TEXT,
    deployment_type VARCHAR(50) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER,
    environment VARCHAR(50) NOT NULL,
    config JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'unknown',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Monitoring configurations
CREATE TABLE monitoring_configs (
    agent_id VARCHAR(255) PRIMARY KEY REFERENCES agents(id) ON DELETE CASCADE,
    metrics_interval_seconds INTEGER DEFAULT 60,
    health_check_interval_seconds INTEGER DEFAULT 30,
    enable_resource_monitoring BOOLEAN DEFAULT TRUE,
    enable_performance_monitoring BOOLEAN DEFAULT TRUE,
    enable_ai_monitoring BOOLEAN DEFAULT FALSE,
    thresholds JSONB DEFAULT '{}',
    retention_settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alerts table
CREATE TABLE alerts (
    id VARCHAR(255) PRIMARY KEY,
    agent_id VARCHAR(255) REFERENCES agents(id) ON DELETE CASCADE,
    severity VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    metric_name VARCHAR(255),
    threshold FLOAT,
    current_value FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- System events
CREATE TABLE system_events (
    id VARCHAR(255) PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    agent_id VARCHAR(255) REFERENCES agents(id) ON DELETE SET NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data JSONB DEFAULT '{}',
    severity VARCHAR(50) DEFAULT 'info',
    message TEXT NOT NULL,
    source VARCHAR(255) DEFAULT 'monitor_system'
);

-- Indexes for performance
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_environment ON agents(environment);
CREATE INDEX idx_agents_last_seen ON agents(last_seen);
CREATE INDEX idx_alerts_agent_id ON alerts(agent_id);
CREATE INDEX idx_alerts_is_active ON alerts(is_active);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);
CREATE INDEX idx_system_events_timestamp ON system_events(timestamp);
CREATE INDEX idx_system_events_type ON system_events(type);
```

### InfluxDB Schema (Time Series Metrics)

```sql
-- Measurement: agent_metrics
-- Tags: agent_id, environment, deployment_type
-- Fields: All numeric metrics
-- Time: timestamp

-- Example queries:
-- SELECT mean("cpu_usage_percent") FROM "agent_metrics" 
-- WHERE "agent_id" = 'agent-123' AND time >= now() - 1h 
-- GROUP BY time(5m)

-- SELECT "tasks_completed", "tasks_failed" FROM "agent_metrics" 
-- WHERE "environment" = 'production' AND time >= now() - 24h
```

This comprehensive data model provides a solid foundation for the agent monitoring system with proper validation, relationships, and scalability considerations.