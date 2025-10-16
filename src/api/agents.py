"""
Agents API Router - Handles agent registration and management.
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse

from ..models import (
    AgentInfo, AgentSummary, AgentMetrics, RegisterResponse,
    AgentStatus, AgentType, DeploymentType
)
from ..core.agent_registry import agent_registry
from ..core.metrics_collector import metrics_collector

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
async def register_agent(agent_info: AgentInfo):
    """Register a new agent"""
    try:
        response = await agent_registry.register_agent(agent_info)
        
        # Start metrics collection for the new agent
        if response.status == "success":
            await metrics_collector.start_collection_for_agent(
                response.agent_id, agent_info
            )
        
        return response
    except Exception as e:
        logger.error(f"Failed to register agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to register agent")


@router.delete("/{agent_id}")
async def deregister_agent(agent_id: str):
    """Deregister an agent"""
    try:
        # Stop metrics collection
        await metrics_collector.stop_collection_for_agent(agent_id)
        
        # Remove from registry
        success = await agent_registry.deregister_agent(agent_id)
        
        if success:
            return {"status": "success", "message": f"Agent {agent_id} deregistered"}
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deregister agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to deregister agent")


@router.get("/", response_model=List[AgentSummary])
async def list_agents(
    environment: Optional[str] = Query(None, description="Filter by environment"),
    agent_type: Optional[AgentType] = Query(None, description="Filter by agent type"),
    status: Optional[AgentStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of agents to return")
):
    """Get list of all registered agents"""
    try:
        # Get all agents
        if environment:
            agents = await agent_registry.get_agents_by_environment(environment)
        elif agent_type:
            agents = await agent_registry.get_agents_by_type(agent_type.value)
        else:
            agents = await agent_registry.get_all_agents()
        
        # Filter by status if specified
        if status:
            agents = [agent for agent in agents if agent.status == status]
        
        # Convert to summaries
        summaries = []
        for agent in agents[:limit]:
            summary = await agent_registry.get_agent_summary(agent.id)
            if summary:
                summaries.append(summary)
        
        return summaries
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail="Failed to list agents")


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    """Get detailed information about a specific agent"""
    try:
        agent = await agent_registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent")


@router.put("/{agent_id}/status")
async def update_agent_status(agent_id: str, status: AgentStatus = Body(...)):
    """Update agent status"""
    try:
        agent = await agent_registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        await agent_registry.update_agent_status(agent_id, status)
        return {"status": "success", "message": f"Agent {agent_id} status updated to {status}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agent status {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update agent status")


@router.post("/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str):
    """Record heartbeat from agent"""
    try:
        success = await agent_registry.record_heartbeat(agent_id)
        if success:
            return {"status": "success", "timestamp": datetime.utcnow()}
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record heartbeat for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to record heartbeat")


@router.post("/{agent_id}/metrics")
async def receive_agent_metrics(agent_id: str, metrics: AgentMetrics):
    """Receive metrics from agent"""
    try:
        # Verify agent exists
        agent = await agent_registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Ensure agent_id matches
        metrics.agent_id = agent_id
        
        # Process metrics
        await metrics_collector.receive_metrics(metrics)
        
        return {"status": "success", "message": "Metrics received"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to receive metrics from {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to receive metrics")


@router.get("/{agent_id}/summary")
async def get_agent_summary(agent_id: str):
    """Get agent summary with recent metrics"""
    try:
        # Get agent info
        agent = await agent_registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get agent summary
        summary = await agent_registry.get_agent_summary(agent_id)
        
        # Get recent metrics
        recent_metrics = await metrics_collector.get_recent_metrics(agent_id, 5)
        
        # Get metrics summary
        metrics_summary = await metrics_collector.get_metrics_summary(agent_id)
        
        return {
            "agent": summary,
            "recent_metrics": recent_metrics,
            "metrics_summary": metrics_summary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent summary {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent summary")