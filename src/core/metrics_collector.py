"""
Metrics Collection Engine - Collects and processes agent metrics.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque

from ..models import AgentMetrics, AgentInfo
from ..config import settings

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and processes agent metrics"""
    
    def __init__(self):
        # In-memory storage for recent metrics (for real-time dashboard)
        self._recent_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self._metric_aggregates: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._collection_tasks: Dict[str, asyncio.Task] = {}
    
    async def collect_metrics_from_agent(self, agent_id: str, agent_info: AgentInfo) -> Optional[AgentMetrics]:
        """Pull metrics from a specific agent"""
        try:
            # This would typically make an HTTP request to the agent's metrics endpoint
            # For now, we'll simulate metrics collection
            
            logger.debug(f"Collecting metrics from agent {agent_id}")
            
            # TODO: Implement actual HTTP client to pull metrics
            # Example:
            # async with httpx.AsyncClient() as client:
            #     response = await client.get(f"http://{agent_info.host}:{agent_info.port}/metrics")
            #     metrics_data = response.json()
            #     return AgentMetrics.parse_obj(metrics_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to collect metrics from agent {agent_id}: {e}")
            return None
    
    async def receive_metrics(self, metrics: AgentMetrics):
        """Receive pushed metrics from agent"""
        try:
            # Store in recent metrics for real-time access
            self._recent_metrics[metrics.agent_id].append(metrics)
            
            # Update aggregates
            await self._update_aggregates(metrics)
            
            # Store in persistent storage (time series database)
            await self._store_metrics_persistent(metrics)
            
            # Check for threshold violations
            await self._check_thresholds(metrics)
            
            logger.debug(f"Received metrics from agent {metrics.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to process metrics from {metrics.agent_id}: {e}")
    
    async def get_recent_metrics(self, agent_id: str, limit: int = 10) -> List[AgentMetrics]:
        """Get recent metrics for an agent"""
        if agent_id not in self._recent_metrics:
            return []
        
        recent = list(self._recent_metrics[agent_id])
        return recent[-limit:] if len(recent) > limit else recent
    
    async def get_metrics_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get summarized metrics for an agent"""
        if agent_id not in self._metric_aggregates:
            return {}
        
        return self._metric_aggregates[agent_id]
    
    async def get_system_metrics_summary(self) -> Dict[str, Any]:
        """Get system-wide metrics summary"""
        total_agents = len(self._recent_metrics)
        total_metrics_points = sum(len(deque_) for deque_ in self._recent_metrics.values())
        
        # Calculate system-wide averages
        system_summary = {
            "total_agents": total_agents,
            "total_metrics_points": total_metrics_points,
            "average_cpu_usage": 0.0,
            "average_memory_usage": 0.0,
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
            "average_response_time": 0.0,
            "system_error_rate": 0.0
        }
        
        if total_agents == 0:
            return system_summary
        
        cpu_sum = memory_sum = tasks_completed_sum = tasks_failed_sum = response_time_sum = 0
        agent_count = 0
        
        for agent_id, aggregates in self._metric_aggregates.items():
            if aggregates:
                cpu_sum += aggregates.get("avg_cpu_usage", 0)
                memory_sum += aggregates.get("avg_memory_usage", 0)
                tasks_completed_sum += aggregates.get("total_tasks_completed", 0)
                tasks_failed_sum += aggregates.get("total_tasks_failed", 0)
                response_time_sum += aggregates.get("avg_response_time", 0)
                agent_count += 1
        
        if agent_count > 0:
            system_summary.update({
                "average_cpu_usage": cpu_sum / agent_count,
                "average_memory_usage": memory_sum / agent_count,
                "total_tasks_completed": tasks_completed_sum,
                "total_tasks_failed": tasks_failed_sum,
                "average_response_time": response_time_sum / agent_count,
                "system_error_rate": (tasks_failed_sum / max(1, tasks_completed_sum + tasks_failed_sum))
            })
        
        return system_summary
    
    async def start_collection_for_agent(self, agent_id: str, agent_info: AgentInfo):
        """Start periodic metrics collection for an agent"""
        async def collect_periodically():
            while agent_id in self._collection_tasks:
                try:
                    metrics = await self.collect_metrics_from_agent(agent_id, agent_info)
                    if metrics:
                        await self.receive_metrics(metrics)
                    
                    await asyncio.sleep(settings.monitoring.default_metrics_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in periodic collection for agent {agent_id}: {e}")
                    await asyncio.sleep(60)  # Wait before retrying
        
        task = asyncio.create_task(collect_periodically())
        self._collection_tasks[agent_id] = task
        logger.info(f"Started metrics collection for agent {agent_id}")
    
    async def stop_collection_for_agent(self, agent_id: str):
        """Stop metrics collection for an agent"""
        if agent_id in self._collection_tasks:
            self._collection_tasks[agent_id].cancel()
            del self._collection_tasks[agent_id]
            logger.info(f"Stopped metrics collection for agent {agent_id}")
    
    async def _update_aggregates(self, metrics: AgentMetrics):
        """Update running aggregates for an agent"""
        agent_id = metrics.agent_id
        
        if agent_id not in self._metric_aggregates:
            self._metric_aggregates[agent_id] = {
                "count": 0,
                "avg_cpu_usage": 0.0,
                "avg_memory_usage": 0.0,
                "avg_response_time": 0.0,
                "total_tasks_completed": 0,
                "total_tasks_failed": 0,
                "last_updated": datetime.utcnow()
            }
        
        agg = self._metric_aggregates[agent_id]
        count = agg["count"]
        
        # Update running averages
        agg["avg_cpu_usage"] = (
            (agg["avg_cpu_usage"] * count + metrics.resource_metrics.cpu_usage_percent) / (count + 1)
        )
        agg["avg_memory_usage"] = (
            (agg["avg_memory_usage"] * count + metrics.resource_metrics.memory_usage_percent) / (count + 1)
        )
        agg["avg_response_time"] = (
            (agg["avg_response_time"] * count + metrics.performance_metrics.average_response_time_ms) / (count + 1)
        )
        
        # Update totals
        agg["total_tasks_completed"] += metrics.performance_metrics.tasks_completed
        agg["total_tasks_failed"] += metrics.performance_metrics.tasks_failed
        
        agg["count"] = count + 1
        agg["last_updated"] = datetime.utcnow()
    
    async def _store_metrics_persistent(self, metrics: AgentMetrics):
        """Store metrics in persistent time series database"""
        try:
            # TODO: Implement InfluxDB storage
            # This would write the metrics to InfluxDB for historical analysis
            
            # Example InfluxDB write:
            # point = Point("agent_metrics") \
            #     .tag("agent_id", metrics.agent_id) \
            #     .field("cpu_usage", metrics.resource_metrics.cpu_usage_percent) \
            #     .field("memory_usage", metrics.resource_metrics.memory_usage_percent) \
            #     .time(metrics.timestamp)
            # await self.influx_client.write_api().write(bucket="metrics", record=point)
            
            pass
            
        except Exception as e:
            logger.error(f"Failed to store metrics in persistent storage: {e}")
    
    async def _check_thresholds(self, metrics: AgentMetrics):
        """Check if any metrics exceed defined thresholds"""
        try:
            alerts = []
            
            # CPU threshold check
            if metrics.resource_metrics.cpu_usage_percent > settings.monitoring.default_cpu_threshold:
                alerts.append(f"High CPU usage: {metrics.resource_metrics.cpu_usage_percent:.1f}%")
            
            # Memory threshold check
            if metrics.resource_metrics.memory_usage_percent > settings.monitoring.default_memory_threshold:
                alerts.append(f"High memory usage: {metrics.resource_metrics.memory_usage_percent:.1f}%")
            
            # Error rate threshold check
            if metrics.performance_metrics.error_rate > settings.monitoring.default_error_rate_threshold:
                alerts.append(f"High error rate: {metrics.performance_metrics.error_rate:.2%}")
            
            # Response time threshold check
            if metrics.performance_metrics.average_response_time_ms > settings.monitoring.default_response_time_threshold:
                alerts.append(f"High response time: {metrics.performance_metrics.average_response_time_ms:.1f}ms")
            
            if alerts:
                logger.warning(f"Threshold violations for agent {metrics.agent_id}: {', '.join(alerts)}")
                # TODO: Send alerts to alerting system
            
        except Exception as e:
            logger.error(f"Failed to check thresholds for {metrics.agent_id}: {e}")


# Global metrics collector instance
metrics_collector = MetricsCollector()