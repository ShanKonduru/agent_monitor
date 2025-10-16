"""
Agent Registry Service - Manages agent registration and discovery.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from ..models import AgentInfo, AgentStatus, AgentSummary, RegisterResponse
from ..config import settings

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Manages agent registration and discovery"""
    
    def __init__(self):
        self._agents: Dict[str, AgentInfo] = {}
        self._agent_last_heartbeat: Dict[str, datetime] = {}
        self._background_tasks: Dict[str, asyncio.Task] = {}
    
    async def register_agent(self, agent_info: AgentInfo) -> RegisterResponse:
        """Register a new agent instance"""
        try:
            # Generate unique ID if not provided
            if not agent_info.id:
                agent_info.id = str(uuid4())
            
            # Set registration timestamp
            agent_info.registered_at = datetime.utcnow()
            agent_info.last_seen = datetime.utcnow()
            agent_info.status = AgentStatus.ONLINE
            
            # Store agent info
            self._agents[agent_info.id] = agent_info
            self._agent_last_heartbeat[agent_info.id] = datetime.utcnow()
            
            # Start monitoring task for this agent
            await self._start_agent_monitoring(agent_info.id)
            
            logger.info(f"Agent registered: {agent_info.id} - {agent_info.name}")
            
            return RegisterResponse(
                agent_id=agent_info.id,
                status="success",
                message=f"Agent {agent_info.name} registered successfully",
                monitoring_endpoints={
                    "metrics": f"/api/v1/agents/{agent_info.id}/metrics",
                    "health": f"/api/v1/agents/{agent_info.id}/health",
                    "heartbeat": f"/api/v1/agents/{agent_info.id}/heartbeat"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            return RegisterResponse(
                agent_id="",
                status="error",
                message=f"Registration failed: {str(e)}",
                monitoring_endpoints={}
            )
    
    async def deregister_agent(self, agent_id: str) -> bool:
        """Remove agent from registry"""
        try:
            if agent_id in self._agents:
                # Stop monitoring task
                if agent_id in self._background_tasks:
                    self._background_tasks[agent_id].cancel()
                    del self._background_tasks[agent_id]
                
                # Remove from registry
                del self._agents[agent_id]
                if agent_id in self._agent_last_heartbeat:
                    del self._agent_last_heartbeat[agent_id]
                
                logger.info(f"Agent deregistered: {agent_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to deregister agent {agent_id}: {e}")
            return False
    
    async def get_active_agents(self) -> List[AgentInfo]:
        """Get list of all active agents"""
        return [agent for agent in self._agents.values() 
                if agent.status in [AgentStatus.ONLINE, AgentStatus.WARNING]]
    
    async def get_all_agents(self) -> List[AgentInfo]:
        """Get list of all registered agents"""
        return list(self._agents.values())
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get specific agent by ID"""
        return self._agents.get(agent_id)
    
    async def get_agent_summary(self, agent_id: str) -> Optional[AgentSummary]:
        """Get agent summary for dashboard"""
        agent = self._agents.get(agent_id)
        if not agent:
            return None
        
        # Calculate health score (simplified for now)
        health_score = self._calculate_health_score(agent)
        
        return AgentSummary(
            id=agent.id,
            name=agent.name,
            type=agent.type,
            status=agent.status,
            last_seen=agent.last_seen,
            environment=agent.environment,
            health_score=health_score
        )
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus):
        """Update agent health status"""
        if agent_id in self._agents:
            self._agents[agent_id].status = status
            self._agents[agent_id].last_seen = datetime.utcnow()
            logger.debug(f"Agent {agent_id} status updated to {status}")
    
    async def record_heartbeat(self, agent_id: str) -> bool:
        """Record heartbeat from agent"""
        if agent_id in self._agents:
            self._agent_last_heartbeat[agent_id] = datetime.utcnow()
            self._agents[agent_id].last_seen = datetime.utcnow()
            
            # Update status to online if it was offline
            if self._agents[agent_id].status == AgentStatus.OFFLINE:
                await self.update_agent_status(agent_id, AgentStatus.ONLINE)
            
            return True
        return False
    
    async def get_agents_by_environment(self, environment: str) -> List[AgentInfo]:
        """Get agents filtered by environment"""
        return [agent for agent in self._agents.values() 
                if agent.environment == environment]
    
    async def get_agents_by_type(self, agent_type: str) -> List[AgentInfo]:
        """Get agents filtered by type"""
        return [agent for agent in self._agents.values() 
                if agent.type == agent_type]
    
    def _calculate_health_score(self, agent: AgentInfo) -> float:
        """Calculate health score for an agent (0.0 - 1.0)"""
        # Simple health score calculation
        # This can be enhanced with more sophisticated metrics
        
        if agent.status == AgentStatus.ONLINE:
            base_score = 1.0
        elif agent.status == AgentStatus.WARNING:
            base_score = 0.7
        elif agent.status == AgentStatus.ERROR:
            base_score = 0.3
        elif agent.status == AgentStatus.OFFLINE:
            base_score = 0.0
        else:
            base_score = 0.5
        
        # Adjust based on last seen time
        time_since_last_seen = datetime.utcnow() - agent.last_seen
        if time_since_last_seen > timedelta(minutes=5):
            base_score *= 0.8
        elif time_since_last_seen > timedelta(minutes=2):
            base_score *= 0.9
        
        return max(0.0, min(1.0, base_score))
    
    async def _start_agent_monitoring(self, agent_id: str):
        """Start background monitoring task for an agent"""
        async def monitor_agent():
            while agent_id in self._agents:
                try:
                    await self._check_agent_health(agent_id)
                    await asyncio.sleep(settings.monitoring.default_health_check_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error monitoring agent {agent_id}: {e}")
                    await asyncio.sleep(30)  # Wait before retrying
        
        task = asyncio.create_task(monitor_agent())
        self._background_tasks[agent_id] = task
    
    async def _check_agent_health(self, agent_id: str):
        """Check if agent is still responsive"""
        if agent_id not in self._agent_last_heartbeat:
            return
        
        last_heartbeat = self._agent_last_heartbeat[agent_id]
        time_since_heartbeat = datetime.utcnow() - last_heartbeat
        
        # Define timeouts
        warning_timeout = timedelta(minutes=2)
        error_timeout = timedelta(minutes=5)
        offline_timeout = timedelta(minutes=10)
        
        current_status = self._agents[agent_id].status
        
        if time_since_heartbeat > offline_timeout:
            if current_status != AgentStatus.OFFLINE:
                await self.update_agent_status(agent_id, AgentStatus.OFFLINE)
                logger.warning(f"Agent {agent_id} marked as OFFLINE")
        elif time_since_heartbeat > error_timeout:
            if current_status not in [AgentStatus.ERROR, AgentStatus.OFFLINE]:
                await self.update_agent_status(agent_id, AgentStatus.ERROR)
                logger.warning(f"Agent {agent_id} marked as ERROR")
        elif time_since_heartbeat > warning_timeout:
            if current_status == AgentStatus.ONLINE:
                await self.update_agent_status(agent_id, AgentStatus.WARNING)
                logger.info(f"Agent {agent_id} marked as WARNING")
        else:
            if current_status != AgentStatus.ONLINE:
                await self.update_agent_status(agent_id, AgentStatus.ONLINE)
                logger.info(f"Agent {agent_id} back ONLINE")


# Global registry instance
agent_registry = AgentRegistry()