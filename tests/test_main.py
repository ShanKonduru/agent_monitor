
"""
Test suite for Agent Monitor Framework.
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.models import (
    AgentInfo, AgentType, DeploymentType, AgentStatus,
    ResourceMetrics, PerformanceMetrics, AgentMetrics
)
from src.core.agent_registry import AgentRegistry
from src.core.metrics_collector import MetricsCollector
from src.agents.client import AgentConfig, AgentMonitorClient


class TestAgentModels:
    """Test agent data models"""
    
    @pytest.mark.unit
    def test_agent_info_creation(self):
        """Test AgentInfo model creation"""
        agent_info = AgentInfo(
            name="Test Agent",
            type=AgentType.LLM_AGENT,
            version="1.0.0",
            deployment_type=DeploymentType.LOCAL,
            host="localhost",
            environment="test"
        )
        
        assert agent_info.name == "Test Agent"
        assert agent_info.type == AgentType.LLM_AGENT
        assert agent_info.status == AgentStatus.UNKNOWN
        assert isinstance(agent_info.id, str)
        assert len(agent_info.id) > 0
    
    @pytest.mark.unit
    def test_resource_metrics_validation(self):
        """Test ResourceMetrics validation"""
        # Valid metrics
        metrics = ResourceMetrics(
            cpu_usage_percent=75.5,
            memory_usage_bytes=1024*1024*512,  # 512MB
            memory_usage_percent=50.0,
            disk_usage_bytes=1024*1024*1024*10  # 10GB
        )
        
        assert metrics.cpu_usage_percent == 75.5
        assert metrics.memory_usage_percent == 50.0
        
        # Test validation boundaries
        with pytest.raises(ValueError):
            ResourceMetrics(
                cpu_usage_percent=150.0,  # Invalid: > 100
                memory_usage_bytes=1024,
                memory_usage_percent=50.0,
                disk_usage_bytes=1024
            )
    
    @pytest.mark.unit
    def test_performance_metrics(self):
        """Test PerformanceMetrics model"""
        metrics = PerformanceMetrics(
            tasks_completed=100,
            tasks_failed=5,
            average_response_time_ms=250.5,
            throughput_per_second=10.5
        )
        
        assert metrics.tasks_completed == 100
        assert metrics.tasks_failed == 5
        assert metrics.error_rate == 0.0  # Default value
        assert metrics.success_rate == 1.0  # Default value


class TestAgentRegistry:
    """Test agent registration and management"""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh agent registry for testing"""
        return AgentRegistry()
    
    @pytest.fixture
    def sample_agent(self):
        """Create a sample agent for testing"""
        return AgentInfo(
            name="Test Agent",
            type=AgentType.CUSTOM,
            version="1.0.0",
            deployment_type=DeploymentType.LOCAL,
            host="localhost",
            environment="test"
        )
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_agent_registration(self, registry, sample_agent):
        """Test agent registration"""
        response = await registry.register_agent(sample_agent)
        
        assert response.status == "success"
        assert response.agent_id == sample_agent.id
        assert "successfully" in response.message.lower()
        assert len(response.monitoring_endpoints) > 0
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_agent_deregistration(self, registry, sample_agent):
        """Test agent deregistration"""
        # Register first
        await registry.register_agent(sample_agent)
        
        # Then deregister
        success = await registry.deregister_agent(sample_agent.id)
        assert success
        
        # Verify agent is gone
        agent = await registry.get_agent(sample_agent.id)
        assert agent is None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_heartbeat_recording(self, registry, sample_agent):
        """Test heartbeat recording"""
        await registry.register_agent(sample_agent)
        
        success = await registry.record_heartbeat(sample_agent.id)
        assert success
        
        # Test non-existent agent
        success = await registry.record_heartbeat("non-existent")
        assert not success
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_agents_by_environment(self, registry):
        """Test filtering agents by environment"""
        # Create agents in different environments
        agent1 = AgentInfo(
            name="Prod Agent",
            type=AgentType.LLM_AGENT,
            version="1.0.0",
            deployment_type=DeploymentType.DOCKER,
            host="prod-host",
            environment="production"
        )
        
        agent2 = AgentInfo(
            name="Dev Agent",
            type=AgentType.API_AGENT,
            version="1.0.0",
            deployment_type=DeploymentType.LOCAL,
            host="dev-host",
            environment="development"
        )
        
        await registry.register_agent(agent1)
        await registry.register_agent(agent2)
        
        prod_agents = await registry.get_agents_by_environment("production")
        dev_agents = await registry.get_agents_by_environment("development")
        
        assert len(prod_agents) == 1
        assert len(dev_agents) == 1
        assert prod_agents[0].name == "Prod Agent"
        assert dev_agents[0].name == "Dev Agent"


class TestMetricsCollector:
    """Test metrics collection and processing"""
    
    @pytest.fixture
    def collector(self):
        """Create a fresh metrics collector for testing"""
        return MetricsCollector()
    
    @pytest.fixture
    def sample_metrics(self):
        """Create sample metrics for testing"""
        return AgentMetrics(
            agent_id="test-agent-123",
            resource_metrics=ResourceMetrics(
                cpu_usage_percent=45.5,
                memory_usage_bytes=1024*1024*256,
                memory_usage_percent=25.0,
                disk_usage_bytes=1024*1024*1024*5
            ),
            performance_metrics=PerformanceMetrics(
                tasks_completed=50,
                tasks_failed=2,
                average_response_time_ms=150.0,
                throughput_per_second=5.0
            )
        )
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_receive_metrics(self, collector, sample_metrics):
        """Test receiving and storing metrics"""
        await collector.receive_metrics(sample_metrics)
        
        recent = await collector.get_recent_metrics("test-agent-123", 1)
        assert len(recent) == 1
        assert recent[0].agent_id == "test-agent-123"
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_metrics_aggregation(self, collector, sample_metrics):
        """Test metrics aggregation"""
        # Send multiple metrics
        for i in range(5):
            metrics = sample_metrics.copy()
            metrics.resource_metrics.cpu_usage_percent = 40.0 + i * 5  # 40, 45, 50, 55, 60
            await collector.receive_metrics(metrics)
        
        summary = await collector.get_metrics_summary("test-agent-123")
        
        assert summary["count"] == 5
        assert summary["avg_cpu_usage"] == 50.0  # Average of 40, 45, 50, 55, 60
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_system_metrics_summary(self, collector):
        """Test system-wide metrics summary"""
        # Add metrics for multiple agents
        for i in range(3):
            metrics = AgentMetrics(
                agent_id=f"agent-{i}",
                resource_metrics=ResourceMetrics(
                    cpu_usage_percent=50.0 + i * 10,
                    memory_usage_bytes=1024*1024*100,
                    memory_usage_percent=30.0,
                    disk_usage_bytes=1024*1024*1024
                ),
                performance_metrics=PerformanceMetrics(
                    tasks_completed=100,
                    tasks_failed=5
                )
            )
            await collector.receive_metrics(metrics)
        
        system_summary = await collector.get_system_metrics_summary()
        
        assert system_summary["total_agents"] == 3
        assert system_summary["average_cpu_usage"] == 60.0  # Average of 50, 60, 70


class TestAgentClient:
    """Test agent monitoring client"""
    
    @pytest.fixture
    def client_config(self):
        """Create client configuration for testing"""
        return AgentConfig(
            monitor_url="http://localhost:8000",
            agent_name="Test Client Agent",
            agent_type=AgentType.CUSTOM,
            environment="test"
        )
    
    @pytest.mark.unit
    def test_client_config_creation(self, client_config):
        """Test client configuration"""
        assert client_config.agent_name == "Test Client Agent"
        assert client_config.agent_type == AgentType.CUSTOM
        assert client_config.environment == "test"
        assert client_config.tags == []  # Default empty list
    
    @pytest.mark.unit
    def test_client_initialization(self, client_config):
        """Test client initialization"""
        client = AgentMonitorClient(client_config)
        
        assert client.config == client_config
        assert client.agent_id is None
        assert not client.is_monitoring
        assert client._task_counters["completed"] == 0
    
    @pytest.mark.unit
    def test_task_recording(self, client_config):
        """Test task recording functionality"""
        client = AgentMonitorClient(client_config)
        
        # Record completed tasks
        client.record_task_completed(100.0)
        client.record_task_completed(200.0)
        
        assert client._task_counters["completed"] == 2
        assert len(client._response_times) == 2
        assert 100.0 in client._response_times
        
        # Record failed task
        client.record_task_failed()
        assert client._task_counters["failed"] == 1
        
        # Set pending tasks
        client.set_pending_tasks(5)
        assert client._task_counters["pending"] == 5


# Integration tests
class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_agent_lifecycle(self):
        """Test complete agent registration, monitoring, and deregistration"""
        registry = AgentRegistry()
        collector = MetricsCollector()
        
        # Create and register agent
        agent = AgentInfo(
            name="Integration Test Agent",
            type=AgentType.LLM_AGENT,
            version="1.0.0",
            deployment_type=DeploymentType.LOCAL,
            host="localhost",
            environment="test"
        )
        
        response = await registry.register_agent(agent)
        assert response.status == "success"
        
        # Start metrics collection
        await collector.start_collection_for_agent(agent.id, agent)
        
        # Send some metrics
        metrics = AgentMetrics(
            agent_id=agent.id,
            resource_metrics=ResourceMetrics(
                cpu_usage_percent=60.0,
                memory_usage_bytes=1024*1024*512,
                memory_usage_percent=40.0,
                disk_usage_bytes=1024*1024*1024*10
            ),
            performance_metrics=PerformanceMetrics(
                tasks_completed=25,
                tasks_failed=1,
                average_response_time_ms=300.0
            )
        )
        
        await collector.receive_metrics(metrics)
        
        # Verify metrics are stored
        recent = await collector.get_recent_metrics(agent.id, 1)
        assert len(recent) == 1
        
        # Stop collection and deregister
        await collector.stop_collection_for_agent(agent.id)
        success = await registry.deregister_agent(agent.id)
        assert success


# Performance tests
class TestPerformance:
    """Performance tests for the monitoring system"""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_high_volume_metrics(self):
        """Test handling high volume of metrics"""
        collector = MetricsCollector()
        
        # Send many metrics rapidly
        agent_id = "performance-test-agent"
        
        start_time = asyncio.get_event_loop().time()
        
        for i in range(100):
            metrics = AgentMetrics(
                agent_id=agent_id,
                resource_metrics=ResourceMetrics(
                    cpu_usage_percent=50.0 + (i % 50),
                    memory_usage_bytes=1024*1024*100,
                    memory_usage_percent=30.0,
                    disk_usage_bytes=1024*1024*1024
                ),
                performance_metrics=PerformanceMetrics(
                    tasks_completed=i,
                    tasks_failed=i // 10
                )
            )
            await collector.receive_metrics(metrics)
        
        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time
        
        # Should process 100 metrics in reasonable time (< 1 second)
        assert processing_time < 1.0
        
        # Verify all metrics were processed
        recent = await collector.get_recent_metrics(agent_id, 100)
        assert len(recent) == 100
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_many_agents_registration(self):
        """Test registering many agents"""
        registry = AgentRegistry()
        
        agent_count = 50
        start_time = asyncio.get_event_loop().time()
        
        # Register many agents
        for i in range(agent_count):
            agent = AgentInfo(
                name=f"Agent-{i}",
                type=AgentType.CUSTOM,
                version="1.0.0",
                deployment_type=DeploymentType.LOCAL,
                host=f"host-{i}",
                environment="performance-test"
            )
            response = await registry.register_agent(agent)
            assert response.status == "success"
        
        end_time = asyncio.get_event_loop().time()
        registration_time = end_time - start_time
        
        # Should register 50 agents in reasonable time (< 2 seconds)
        assert registration_time < 2.0
        
        # Verify all agents are registered
        all_agents = await registry.get_all_agents()
        perf_agents = [a for a in all_agents if a.environment == "performance-test"]
        assert len(perf_agents) == agent_count
