"""
Agent Registry Service - Manages agent registration and discovery with PostgreSQL persistence.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

from ..models import AgentInfo, AgentStatus, AgentSummary, RegisterResponse, AgentType, DeploymentType
from ..database.models import Agent as DBAgent, AgentTag, AgentConfiguration
from ..database.connection import DatabaseManager
from ..config import settings

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Manages agent registration and discovery with database persistence"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._background_tasks: Dict[str, asyncio.Task] = {}
    
    async def register_agent(self, agent_info: AgentInfo) -> RegisterResponse:
        """Register a new agent instance in database"""
        try:
            # Generate unique ID if not provided
            if not agent_info.id:
                agent_info.id = str(uuid4())
            
            # Convert AgentInfo to database model
            db_agent = DBAgent(
                id=agent_info.id,
                name=agent_info.name,
                type=AgentType(agent_info.type),
                version=agent_info.version,
                description=agent_info.description,
                deployment_type=DeploymentType(agent_info.deployment_type),
                host=agent_info.host,
                port=getattr(agent_info, 'port', None),
                environment=agent_info.environment,
                status=AgentStatus.ONLINE,
                last_heartbeat=datetime.utcnow(),
                agent_metadata=agent_info.metadata or {}
            )
            
            # Store in database
            async with self.db_manager.get_session() as session:
                session.add(db_agent)
                
                # Add tags if provided
                if hasattr(agent_info, 'tags') and agent_info.tags:
                    for tag in agent_info.tags:
                        db_tag = AgentTag(agent_id=agent_info.id, tag=tag)
                        session.add(db_tag)
                
                await session.commit()
                await session.refresh(db_agent)
            
            # Start monitoring task for this agent
            await self._start_agent_monitoring(agent_info.id)
            
            logger.info(f"Agent registered in database: {agent_info.id} - {agent_info.name}")
            
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
            
        except IntegrityError as e:
            logger.error(f"Agent registration failed - duplicate ID: {e}")
            return RegisterResponse(
                agent_id="",
                status="error",
                message=f"Agent with ID {agent_info.id} already exists",
                monitoring_endpoints={}
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
        """Remove agent from database"""
        try:
            async with self.db_manager.get_session() as session:
                # Delete agent from database (cascades to related tables)
                result = await session.execute(
                    delete(DBAgent).where(DBAgent.id == agent_id)
                )
                
                if result.rowcount > 0:
                    await session.commit()
                    
                    # Stop monitoring task
                    if agent_id in self._background_tasks:
                        self._background_tasks[agent_id].cancel()
                        del self._background_tasks[agent_id]
                    
                    logger.info(f"Agent deregistered from database: {agent_id}")
                    return True
                else:
                    logger.warning(f"Agent not found for deregistration: {agent_id}")
                    return False
            
        except Exception as e:
            logger.error(f"Failed to deregister agent {agent_id}: {e}")
            return False
    
    async def get_active_agents(self) -> List[AgentInfo]:
        """Get list of all active agents from database"""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    select(DBAgent).where(
                        DBAgent.status.in_([AgentStatus.ONLINE])
                    )
                )
                db_agents = result.scalars().all()
                return [self._convert_db_agent_to_agent_info(db_agent) for db_agent in db_agents]
        except Exception as e:
            logger.error(f"Failed to get active agents: {e}")
            return []
    
    async def get_all_agents(self) -> List[AgentInfo]:
        """Get list of all registered agents from database"""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(select(DBAgent))
                db_agents = result.scalars().all()
                return [self._convert_db_agent_to_agent_info(db_agent) for db_agent in db_agents]
        except Exception as e:
            logger.error(f"Failed to get all agents: {e}")
            return []
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get specific agent by ID from database"""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    select(DBAgent).where(DBAgent.id == agent_id)
                )
                db_agent = result.scalar_one_or_none()
                
                if db_agent:
                    return self._convert_db_agent_to_agent_info(db_agent)
                return None
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
            return None
    
    def _convert_db_agent_to_agent_info(self, db_agent: DBAgent) -> AgentInfo:
        """Convert database Agent model to AgentInfo"""
        return AgentInfo(
            id=db_agent.id,
            name=db_agent.name,
            type=db_agent.type.value,
            version=db_agent.version,
            description=db_agent.description,
            deployment_type=db_agent.deployment_type.value,
            host=db_agent.host,
            port=db_agent.port,
            environment=db_agent.environment,
            status=db_agent.status,
            registered_at=db_agent.created_at,
            last_seen=db_agent.last_heartbeat or db_agent.updated_at,
            metadata=db_agent.agent_metadata or {}
        )
    
    async def get_agent_summary(self, agent_id: str) -> Optional[AgentSummary]:
        """Get agent summary for dashboard from database"""
        agent = await self.get_agent(agent_id)
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
        """Update agent health status in database"""
        try:
            async with self.db_manager.get_session() as session:
                await session.execute(
                    update(DBAgent)
                    .where(DBAgent.id == agent_id)
                    .values(
                        status=status,
                        last_heartbeat=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                )
                await session.commit()
                logger.debug(f"Agent {agent_id} status updated to {status} in database")
        except Exception as e:
            logger.error(f"Failed to update agent status for {agent_id}: {e}")
    
    async def record_heartbeat(self, agent_id: str) -> bool:
        """Record heartbeat from agent in database"""
        try:
            async with self.db_manager.get_session() as session:
                # Check if agent exists and get current status
                result = await session.execute(
                    select(DBAgent.status).where(DBAgent.id == agent_id)
                )
                current_status = result.scalar_one_or_none()
                
                if current_status is not None:
                    # Update heartbeat
                    await session.execute(
                        update(DBAgent)
                        .where(DBAgent.id == agent_id)
                        .values(
                            last_heartbeat=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                            status=AgentStatus.ONLINE if current_status == AgentStatus.OFFLINE else current_status
                        )
                    )
                    await session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to record heartbeat for {agent_id}: {e}")
            return False
    
    async def get_agents_by_environment(self, environment: str) -> List[AgentInfo]:
        """Get agents filtered by environment from database"""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    select(DBAgent).where(DBAgent.environment == environment)
                )
                db_agents = result.scalars().all()
                return [self._convert_db_agent_to_agent_info(db_agent) for db_agent in db_agents]
        except Exception as e:
            logger.error(f"Failed to get agents by environment {environment}: {e}")
            return []
    
    async def get_agents_by_type(self, agent_type: str) -> List[AgentInfo]:
        """Get agents filtered by type from database"""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    select(DBAgent).where(DBAgent.type == AgentType(agent_type))
                )
                db_agents = result.scalars().all()
                return [self._convert_db_agent_to_agent_info(db_agent) for db_agent in db_agents]
        except Exception as e:
            logger.error(f"Failed to get agents by type {agent_type}: {e}")
            return []
    
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
            while True:
                try:
                    # Check if agent still exists in database
                    agent = await self.get_agent(agent_id)
                    if not agent:
                        break
                    
                    await self._check_agent_health(agent_id)
                    await asyncio.sleep(getattr(settings, 'monitoring', {}).get('default_health_check_interval', 30))
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error monitoring agent {agent_id}: {e}")
                    await asyncio.sleep(30)  # Wait before retrying
        
        task = asyncio.create_task(monitor_agent())
        self._background_tasks[agent_id] = task
    
    async def _check_agent_health(self, agent_id: str):
        """Check if agent is still responsive using database"""
        try:
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    select(DBAgent.last_heartbeat, DBAgent.status)
                    .where(DBAgent.id == agent_id)
                )
                row = result.first()
                
                if not row or not row.last_heartbeat:
                    return
                
                last_heartbeat, current_status = row
                time_since_heartbeat = datetime.utcnow() - last_heartbeat
                
                # Define timeouts
                warning_timeout = timedelta(minutes=2)
                error_timeout = timedelta(minutes=5)
                offline_timeout = timedelta(minutes=10)
                
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
        except Exception as e:
            logger.error(f"Failed to check agent health for {agent_id}: {e}")


# Global registry instance - will be initialized in main_v2.py with database manager
agent_registry = None