"""
Health API Router - Handles health checks and status monitoring.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from ..models import HealthStatus, HealthCheck, Alert, AgentStatus

logger = logging.getLogger(__name__)

router = APIRouter()

# Global registry instance - will be set by main.py
agent_registry = None

def set_agent_registry(registry):
    """Set the agent registry instance"""
    global agent_registry
    agent_registry = registry

def get_agent_registry():
    """Get the current agent registry instance"""
    if agent_registry is None:
        raise HTTPException(status_code=500, detail="Agent registry not initialized")
    return agent_registry


@router.get("/{agent_id}")
async def get_agent_health(agent_id: str):
    """Get health status for a specific agent"""
    try:
        # Get agent registry
        agent_reg = get_agent_registry()
        
        # Verify agent exists
        agent = await agent_reg.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Calculate health score
        health_score = agent_reg._calculate_health_score(agent)
        
        # Mock health checks (in real implementation, these would be actual checks)
        health_checks = [
            HealthCheck(
                name="connectivity",
                status=agent.status in [AgentStatus.ONLINE, AgentStatus.WARNING],
                message="Agent is reachable" if agent.status == AgentStatus.ONLINE else "Agent connectivity issues",
                execution_time_ms=50.0
            ),
            HealthCheck(
                name="response_time",
                status=True,  # Would be based on actual response time metrics
                message="Response time within acceptable limits",
                execution_time_ms=25.0
            ),
            HealthCheck(
                name="error_rate",
                status=True,  # Would be based on actual error rate metrics
                message="Error rate within acceptable limits",
                execution_time_ms=30.0
            )
        ]
        
        # Determine overall status based on individual checks
        overall_status = agent.status
        is_responsive = agent.status in [AgentStatus.ONLINE, AgentStatus.WARNING]
        
        health_status = HealthStatus(
            agent_id=agent_id,
            overall_status=overall_status,
            health_score=health_score,
            checks=health_checks,
            is_responsive=is_responsive,
            last_heartbeat=agent.last_seen,
            uptime_seconds=int((datetime.utcnow() - agent.registered_at).total_seconds())
        )
        
        return health_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get health status for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get health status")


@router.get("/")
async def get_system_health():
    """Get overall system health status"""
    try:
        # Get agent registry
        agent_reg = get_agent_registry()
        
        # Get all agents
        agents = await agent_reg.get_all_agents()
        
        if not agents:
            return {
                "status": "healthy",
                "total_agents": 0,
                "healthy_agents": 0,
                "unhealthy_agents": 0,
                "system_health_score": 1.0,
                "timestamp": datetime.utcnow()
            }
        
        # Calculate health statistics
        total_agents = len(agents)
        healthy_agents = len([a for a in agents if a.status in [AgentStatus.ONLINE, AgentStatus.WARNING]])
        unhealthy_agents = total_agents - healthy_agents
        
        # Calculate system health score
        system_health_score = healthy_agents / total_agents if total_agents > 0 else 1.0
        
        # Determine overall system status
        if system_health_score >= 0.9:
            system_status = "healthy"
        elif system_health_score >= 0.7:
            system_status = "degraded"
        else:
            system_status = "unhealthy"
        
        # Get agent status distribution
        status_distribution = {}
        for status in AgentStatus:
            count = len([a for a in agents if a.status == status])
            status_distribution[status.value] = count
        
        return {
            "status": system_status,
            "total_agents": total_agents,
            "healthy_agents": healthy_agents,
            "unhealthy_agents": unhealthy_agents,
            "system_health_score": system_health_score,
            "status_distribution": status_distribution,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system health")


@router.post("/{agent_id}/check")
async def perform_health_check(agent_id: str):
    """Perform on-demand health check for an agent"""
    try:
        # Get agent registry
        agent_reg = get_agent_registry()
        
        # Verify agent exists
        agent = await agent_reg.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # TODO: Implement actual health check logic
        # This would typically involve making requests to the agent's health endpoint
        
        # Mock health check for now
        check_results = []
        
        # Connectivity check
        connectivity_ok = agent.status != AgentStatus.OFFLINE
        check_results.append(HealthCheck(
            name="connectivity",
            status=connectivity_ok,
            message="Agent is reachable" if connectivity_ok else "Agent is offline",
            execution_time_ms=45.0
        ))
        
        # Response time check (mock)
        response_time_ok = True  # Would be based on actual ping/request
        check_results.append(HealthCheck(
            name="response_time",
            status=response_time_ok,
            message="Response time acceptable" if response_time_ok else "High response time",
            execution_time_ms=120.0
        ))
        
        # Resource usage check (mock)
        resource_ok = True  # Would be based on latest metrics
        check_results.append(HealthCheck(
            name="resources",
            status=resource_ok,
            message="Resource usage normal" if resource_ok else "High resource usage",
            execution_time_ms=80.0
        ))
        
        # Update agent status based on checks
        failed_checks = [check for check in check_results if not check.status]
        
        if len(failed_checks) == 0:
            new_status = AgentStatus.ONLINE
        elif len(failed_checks) == 1:
            new_status = AgentStatus.WARNING
        else:
            new_status = AgentStatus.ERROR
        
        await agent_reg.update_agent_status(agent_id, new_status)
        
        return {
            "agent_id": agent_id,
            "health_check_timestamp": datetime.utcnow(),
            "overall_status": new_status,
            "checks": check_results,
            "failed_checks": len(failed_checks),
            "total_checks": len(check_results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to perform health check for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform health check")


@router.get("/alerts/active")
async def get_active_alerts():
    """Get all active alerts in the system"""
    try:
        # TODO: Implement actual alerts storage and retrieval
        # For now, return mock alerts
        
        mock_alerts = []
        
        # Get agents with issues
        agents = await agent_registry.get_all_agents()
        for agent in agents:
            if agent.status in [AgentStatus.WARNING, AgentStatus.ERROR, AgentStatus.OFFLINE]:
                severity = "critical" if agent.status == AgentStatus.OFFLINE else "warning"
                
                alert = Alert(
                    agent_id=agent.id,
                    severity=severity,
                    title=f"Agent {agent.name} health issue",
                    message=f"Agent {agent.name} is in {agent.status.value} state",
                    created_at=agent.last_seen
                )
                mock_alerts.append(alert)
        
        return {
            "active_alerts": mock_alerts,
            "total_alerts": len(mock_alerts),
            "critical_alerts": len([a for a in mock_alerts if a.severity == "critical"]),
            "warning_alerts": len([a for a in mock_alerts if a.severity == "warning"]),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active alerts")


@router.get("/alerts/{agent_id}")
async def get_agent_alerts(
    agent_id: str,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of alerts to return"),
    active_only: bool = Query(True, description="Return only active alerts")
):
    """Get alerts for a specific agent"""
    try:
        # Verify agent exists
        agent = await agent_registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # TODO: Implement actual alerts storage and retrieval
        # For now, return mock alerts based on agent status
        
        alerts = []
        
        if agent.status != AgentStatus.ONLINE:
            severity = "critical" if agent.status == AgentStatus.OFFLINE else "warning"
            
            alert = Alert(
                agent_id=agent_id,
                severity=severity,
                title=f"Agent health issue",
                message=f"Agent is in {agent.status.value} state",
                created_at=agent.last_seen,
                is_active=True
            )
            alerts.append(alert)
        
        # Filter by active status if requested
        if active_only:
            alerts = [alert for alert in alerts if alert.is_active]
        
        return {
            "agent_id": agent_id,
            "alerts": alerts[:limit],
            "total_alerts": len(alerts),
            "active_alerts": len([a for a in alerts if a.is_active]),
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get alerts for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent alerts")