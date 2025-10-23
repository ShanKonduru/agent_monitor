"""
Python Agent Client Library for Agent Monitor Framework.
"""

import asyncio
import logging
import psutil
import time
import httpx
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

from ..models import (
    AgentInfo, AgentMetrics, ResourceMetrics, PerformanceMetrics, AIMetrics,
    AgentType, DeploymentType, AgentStatus
)

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for agent monitoring client"""
    monitor_url: str
    agent_name: str
    agent_type: AgentType = AgentType.CUSTOM
    deployment_type: DeploymentType = DeploymentType.LOCAL
    environment: str = "development"
    version: str = "1.0.0"
    description: Optional[str] = None
    tags: list = None
    custom_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.custom_metrics is None:
            self.custom_metrics = {}


class AgentMonitorClient:
    """Python client library for agent monitoring"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent_id: Optional[str] = None
        self.is_monitoring = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._start_time = time.time()
        self._task_counters = {
            "completed": 0,
            "failed": 0,
            "pending": 0
        }
        self._response_times = []
        self._custom_metrics_callbacks: Dict[str, Callable] = {}
        
        # HTTP client for API communication
        self._http_client = httpx.AsyncClient(
            base_url=config.monitor_url,
            timeout=30.0
        )
    
    async def register(self) -> bool:
        """Register this agent with the monitor"""
        try:
            # Get system information
            import socket
            hostname = socket.gethostname()
            
            agent_info = AgentInfo(
                name=self.config.agent_name,
                type=self.config.agent_type,
                version=self.config.version,
                description=self.config.description,
                deployment_type=self.config.deployment_type,
                host=hostname,
                environment=self.config.environment,
                tags=self.config.tags,
                config=self.config.custom_metrics
            )
            
            response = await self._http_client.post(
                "/api/v1/agents/register",
                json=agent_info.model_dump(mode='json')
            )
            
            if response.status_code == 200:
                result = response.json()
                self.agent_id = result["agent_id"]
                logger.info(f"Agent registered successfully with ID: {self.agent_id}")
                return True
            else:
                logger.error(f"Failed to register agent: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            return False
    
    async def start_monitoring(self):
        """Start background monitoring tasks"""
        if not self.agent_id:
            if not await self.register():
                raise RuntimeError("Failed to register agent")
        
        if self.is_monitoring:
            logger.warning("Monitoring is already running")
            return
        
        self.is_monitoring = True
        
        # Start metrics collection task
        self._monitoring_task = asyncio.create_task(self._metrics_collection_loop())
        
        # Start heartbeat task
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        logger.info("Agent monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring tasks"""
        self.is_monitoring = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Agent monitoring stopped")
    
    async def send_heartbeat(self) -> bool:
        """Send heartbeat to monitor"""
        if not self.agent_id:
            return False
        
        try:
            response = await self._http_client.post(
                f"/api/v1/agents/{self.agent_id}/heartbeat"
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")
            return False
    
    async def report_metrics(self, custom_metrics: Optional[Dict[str, Any]] = None) -> bool:
        """Report performance metrics"""
        if not self.agent_id:
            return False
        
        try:
            metrics = await self._collect_metrics(custom_metrics)
            
            response = await self._http_client.post(
                f"/api/v1/agents/{self.agent_id}/metrics",
                json=metrics.model_dump(mode='json')
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to report metrics: {e}")
            return False
    
    def register_custom_metric(self, name: str, callback: Callable[[], Any]):
        """Register a custom metric callback"""
        self._custom_metrics_callbacks[name] = callback
    
    def record_task_completed(self, response_time_ms: Optional[float] = None):
        """Record a completed task"""
        self._task_counters["completed"] += 1
        if response_time_ms is not None:
            self._response_times.append(response_time_ms)
            # Keep only last 100 response times
            if len(self._response_times) > 100:
                self._response_times = self._response_times[-100:]
    
    def record_task_failed(self):
        """Record a failed task"""
        self._task_counters["failed"] += 1
    
    def set_pending_tasks(self, count: int):
        """Set the number of pending tasks"""
        self._task_counters["pending"] = count
    
    async def _collect_metrics(self, custom_metrics: Optional[Dict[str, Any]] = None) -> AgentMetrics:
        """Collect current metrics"""
        # Collect system resource metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        
        resource_metrics = ResourceMetrics(
            cpu_usage_percent=cpu_percent,
            memory_usage_bytes=memory.used,
            memory_usage_percent=memory.percent,
            disk_usage_bytes=disk.used,
            disk_io_read_bytes=net_io.bytes_recv if net_io else 0,
            disk_io_write_bytes=net_io.bytes_sent if net_io else 0,
            network_io_rx_bytes=net_io.bytes_recv if net_io else 0,
            network_io_tx_bytes=net_io.bytes_sent if net_io else 0
        )
        
        # Collect performance metrics
        uptime = int(time.time() - self._start_time)
        avg_response_time = (
            sum(self._response_times) / len(self._response_times) 
            if self._response_times else 0.0
        )
        
        total_tasks = self._task_counters["completed"] + self._task_counters["failed"]
        error_rate = (
            self._task_counters["failed"] / total_tasks 
            if total_tasks > 0 else 0.0
        )
        success_rate = 1.0 - error_rate
        
        performance_metrics = PerformanceMetrics(
            tasks_completed=self._task_counters["completed"],
            tasks_failed=self._task_counters["failed"],
            tasks_pending=self._task_counters["pending"],
            average_response_time_ms=avg_response_time,
            throughput_per_second=self._task_counters["completed"] / max(1, uptime),
            error_rate=error_rate,
            success_rate=success_rate,
            uptime_seconds=uptime
        )
        
        # Collect custom metrics
        collected_custom_metrics = custom_metrics or {}
        for name, callback in self._custom_metrics_callbacks.items():
            try:
                collected_custom_metrics[name] = callback()
            except Exception as e:
                logger.error(f"Failed to collect custom metric {name}: {e}")
        
        # Extract AI-specific metrics from custom metrics
        ai_metrics = None
        ai_metric_fields = {}
        
        # Map custom metric names to AIMetrics fields
        ai_metric_mapping = {
            "tokens_processed": "tokens_processed",
            "model_accuracy": "model_accuracy", 
            "model_inference_time_ms": "model_inference_time_ms",
            "tokens_per_second": "tokens_per_second",
            "context_length": "context_length",
            "api_calls_made": "api_calls_made",
            "api_call_latency_ms": "api_call_latency_ms",
            "confidence_score": "confidence_score"
        }
        
        # Extract AI metrics from custom metrics
        for custom_name, ai_field in ai_metric_mapping.items():
            if custom_name in collected_custom_metrics:
                ai_metric_fields[ai_field] = collected_custom_metrics[custom_name]
        
        # Create AIMetrics if we have any AI-specific data
        if ai_metric_fields:
            ai_metrics = AIMetrics(**ai_metric_fields)
        
        # Create metrics object
        metrics = AgentMetrics(
            agent_id=self.agent_id,
            resource_metrics=resource_metrics,
            performance_metrics=performance_metrics,
            ai_metrics=ai_metrics,
            custom_metrics=collected_custom_metrics,
            health_checks={
                "system_health": True,  # Could be more sophisticated
                "connectivity": True
            }
        )
        
        return metrics
    
    async def _metrics_collection_loop(self):
        """Background task for periodic metrics collection"""
        while self.is_monitoring:
            try:
                await self.report_metrics()
                await asyncio.sleep(60)  # Collect metrics every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(60)
    
    async def _heartbeat_loop(self):
        """Background task for periodic heartbeat"""
        while self.is_monitoring:
            try:
                await self.send_heartbeat()
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(30)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_monitoring()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop_monitoring()
        await self._http_client.aclose()


# Convenience function for simple agent setup
async def create_monitored_agent(
    monitor_url: str,
    agent_name: str,
    agent_type: AgentType = AgentType.CUSTOM,
    environment: str = "development"
) -> AgentMonitorClient:
    """Create and register a monitored agent"""
    config = AgentConfig(
        monitor_url=monitor_url,
        agent_name=agent_name,
        agent_type=agent_type,
        environment=environment
    )
    
    client = AgentMonitorClient(config)
    
    if await client.register():
        await client.start_monitoring()
        return client
    else:
        raise RuntimeError("Failed to create monitored agent")