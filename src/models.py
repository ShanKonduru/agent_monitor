"""
Core data models for the Agent Monitor Framework.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class AgentType(str, Enum):
    """Types of agents that can be monitored"""
    LLM_AGENT = "LLM_AGENT"
    TASK_AGENT = "TASK_AGENT"
    API_AGENT = "API_AGENT"
    MONITOR_AGENT = "MONITOR_AGENT"
    DATA_AGENT = "DATA_AGENT"
    CUSTOM = "CUSTOM"


class AgentStatus(str, Enum):
    """Current status of an agent"""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    MAINTENANCE = "MAINTENANCE"
    UNKNOWN = "UNKNOWN"


class DeploymentType(str, Enum):
    """Where the agent is deployed"""
    DOCKER = "DOCKER"
    KUBERNETES = "KUBERNETES"
    LOCAL = "LOCAL"
    CLOUD = "CLOUD"
    SERVERLESS = "SERVERLESS"


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


class RegisterResponse(BaseModel):
    """Response after agent registration"""
    agent_id: str
    status: str
    message: str
    monitoring_endpoints: Dict[str, str]


class MetricsQuery(BaseModel):
    """Query parameters for retrieving metrics"""
    agent_ids: Optional[List[str]] = Field(None, description="Filter by agent IDs")
    start_time: datetime = Field(..., description="Start time for query")
    end_time: datetime = Field(..., description="End time for query")
    metric_names: Optional[List[str]] = Field(None, description="Specific metrics to retrieve")
    aggregation: Optional[str] = Field(None, description="Aggregation method (avg, sum, max, min)")
    interval: Optional[str] = Field(None, description="Time interval for aggregation")


class MetricsResponse(BaseModel):
    """Response for metrics queries"""
    query: MetricsQuery
    total_points: int
    agents: List[str]
    time_range: Dict[str, datetime]
    data: List[Dict[str, Any]]