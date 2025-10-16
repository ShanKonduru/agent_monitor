"""
Metrics API Router - Handles metrics queries and dashboard data.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query

from ..models import MetricsQuery, MetricsResponse, AgentMetrics
from ..core.agent_registry import agent_registry
from ..core.metrics_collector import metrics_collector

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=MetricsResponse)
async def query_metrics(
    agent_ids: Optional[List[str]] = Query(None, description="Filter by agent IDs"),
    start_time: Optional[datetime] = Query(None, description="Start time for query"),
    end_time: Optional[datetime] = Query(None, description="End time for query"),
    metric_names: Optional[List[str]] = Query(None, description="Specific metrics to retrieve"),
    aggregation: Optional[str] = Query(None, description="Aggregation method"),
    interval: Optional[str] = Query(None, description="Time interval for aggregation")
):
    """Query historical metrics"""
    try:
        # Set default time range if not provided
        if not end_time:
            end_time = datetime.utcnow()
        if not start_time:
            start_time = end_time - timedelta(hours=24)
        
        query = MetricsQuery(
            agent_ids=agent_ids,
            start_time=start_time,
            end_time=end_time,
            metric_names=metric_names,
            aggregation=aggregation,
            interval=interval
        )
        
        # TODO: Implement actual time series database query
        # For now, return mock response
        mock_data = []
        agents_list = agent_ids or []
        
        if not agent_ids:
            # Get all agents if none specified
            all_agents = await agent_registry.get_all_agents()
            agents_list = [agent.id for agent in all_agents]
        
        # Get recent metrics for each agent
        for agent_id in agents_list:
            recent_metrics = await metrics_collector.get_recent_metrics(agent_id, 10)
            for metric in recent_metrics:
                mock_data.append({
                    "agent_id": agent_id,
                    "timestamp": metric.timestamp,
                    "cpu_usage": metric.resource_metrics.cpu_usage_percent,
                    "memory_usage": metric.resource_metrics.memory_usage_percent,
                    "tasks_completed": metric.performance_metrics.tasks_completed,
                    "response_time": metric.performance_metrics.average_response_time_ms
                })
        
        return MetricsResponse(
            query=query,
            total_points=len(mock_data),
            agents=agents_list,
            time_range={"start": start_time, "end": end_time},
            data=mock_data
        )
        
    except Exception as e:
        logger.error(f"Failed to query metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to query metrics")


@router.get("/recent/{agent_id}")
async def get_recent_metrics(
    agent_id: str,
    limit: int = Query(10, ge=1, le=100, description="Number of recent metrics to return")
):
    """Get recent metrics for a specific agent"""
    try:
        # Verify agent exists
        agent = await agent_registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        recent_metrics = await metrics_collector.get_recent_metrics(agent_id, limit)
        
        return {
            "agent_id": agent_id,
            "count": len(recent_metrics),
            "metrics": recent_metrics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recent metrics for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recent metrics")


@router.get("/summary/{agent_id}")
async def get_agent_metrics_summary(agent_id: str):
    """Get metrics summary for a specific agent"""
    try:
        # Verify agent exists
        agent = await agent_registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        summary = await metrics_collector.get_metrics_summary(agent_id)
        
        return {
            "agent_id": agent_id,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metrics summary for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics summary")


@router.get("/system/summary")
async def get_system_metrics_summary():
    """Get system-wide metrics summary"""
    try:
        summary = await metrics_collector.get_system_metrics_summary()
        return summary
    except Exception as e:
        logger.error(f"Failed to get system metrics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system metrics summary")


@router.get("/dashboard/data")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        # Get agents summary
        agents = await agent_registry.get_all_agents()
        agents_summary = []
        
        for agent in agents:
            summary = await agent_registry.get_agent_summary(agent.id)
            if summary:
                agents_summary.append(summary)
        
        # Get system metrics
        system_metrics = await metrics_collector.get_system_metrics_summary()
        
        # Calculate additional dashboard stats
        total_agents = len(agents)
        online_agents = len([a for a in agents if a.status == "online"])
        warning_agents = len([a for a in agents if a.status == "warning"])
        error_agents = len([a for a in agents if a.status == "error"])
        offline_agents = len([a for a in agents if a.status == "offline"])
        
        # Get environment distribution
        environments = {}
        for agent in agents:
            env = agent.environment
            environments[env] = environments.get(env, 0) + 1
        
        # Get agent type distribution
        agent_types = {}
        for agent in agents:
            agent_type = agent.type.value
            agent_types[agent_type] = agent_types.get(agent_type, 0) + 1
        
        dashboard_data = {
            "timestamp": datetime.utcnow(),
            "overview": {
                "total_agents": total_agents,
                "online_agents": online_agents,
                "warning_agents": warning_agents,
                "error_agents": error_agents,
                "offline_agents": offline_agents,
                "health_score": (online_agents / max(1, total_agents)) * 100
            },
            "agents": agents_summary,
            "system_metrics": system_metrics,
            "distributions": {
                "environments": environments,
                "agent_types": agent_types
            }
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")


@router.get("/agents/{agent_id}/trends")
async def get_agent_trends(
    agent_id: str,
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze")
):
    """Get performance trends for a specific agent"""
    try:
        # Verify agent exists
        agent = await agent_registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get recent metrics
        recent_metrics = await metrics_collector.get_recent_metrics(agent_id, hours * 6)  # Assuming 10-minute intervals
        
        if not recent_metrics:
            return {
                "agent_id": agent_id,
                "trends": {
                    "cpu_trend": "stable",
                    "memory_trend": "stable",
                    "performance_trend": "stable"
                },
                "data_points": 0
            }
        
        # Calculate trends (simplified)
        cpu_values = [m.resource_metrics.cpu_usage_percent for m in recent_metrics]
        memory_values = [m.resource_metrics.memory_usage_percent for m in recent_metrics]
        response_times = [m.performance_metrics.average_response_time_ms for m in recent_metrics]
        
        def calculate_trend(values):
            if len(values) < 2:
                return "stable"
            
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            
            change_percent = ((avg_second - avg_first) / avg_first) * 100
            
            if change_percent > 10:
                return "increasing"
            elif change_percent < -10:
                return "decreasing"
            else:
                return "stable"
        
        trends = {
            "agent_id": agent_id,
            "trends": {
                "cpu_trend": calculate_trend(cpu_values),
                "memory_trend": calculate_trend(memory_values),
                "performance_trend": calculate_trend(response_times)
            },
            "data_points": len(recent_metrics),
            "time_range_hours": hours
        }
        
        return trends
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get trends for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent trends")