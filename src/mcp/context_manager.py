"""
MCP Context Manager
Manages shared context and state between AI providers and agents
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import asdict

from .protocol import ContextData, MCPMessage, AgentInfo, AgentType
from .memory_store import MemoryStore

logger = logging.getLogger(__name__)

class ContextManager:
    """Manages context sharing between agents and AI providers"""
    
    def __init__(self, memory_store: Optional[MemoryStore] = None):
        """Initialize context manager"""
        self.memory_store = memory_store or MemoryStore()
        self.active_contexts: Dict[str, ContextData] = {}
        self.registered_agents: Dict[str, AgentInfo] = {}
        logger.info("ContextManager initialized")
    
    def register_agent(self, agent_id: str, agent_type: AgentType, name: str, 
                      capabilities: List[str] = None, metadata: Dict[str, Any] = None) -> bool:
        """Register an agent with the context manager"""
        agent_info = AgentInfo(
            agent_id=agent_id,
            agent_type=agent_type,
            name=name,
            capabilities=capabilities or [],
            metadata=metadata or {}
        )
        
        self.registered_agents[agent_id] = agent_info
        
        # Store in memory
        success = self.memory_store.store_agent(agent_info)
        
        if success:
            logger.info(f"Registered agent {agent_id} ({agent_type.value}): {name}")
        else:
            logger.error(f"Failed to register agent {agent_id}")
        
        return success
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent"""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            logger.info(f"Unregistered agent {agent_id}")
            return True
        return False
    
    def update_agent_status(self, agent_id: str, status: str, metadata: Dict[str, Any] = None) -> bool:
        """Update agent status"""
        agent = self.registered_agents.get(agent_id)
        if agent:
            agent.status = status
            agent.last_seen = datetime.now()
            if metadata:
                agent.metadata.update(metadata)
            
            # Update in memory store
            return self.memory_store.store_agent(agent)
        return False
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent information"""
        # Check active agents first
        if agent_id in self.registered_agents:
            return self.registered_agents[agent_id]
        
        # Try to load from memory store
        agent = self.memory_store.get_agent(agent_id)
        if agent:
            self.registered_agents[agent_id] = agent
        
        return agent
    
    def list_agents(self, agent_type: Optional[AgentType] = None, status: Optional[str] = None) -> List[AgentInfo]:
        """List registered agents"""
        agents = list(self.registered_agents.values())
        
        # Load additional agents from memory store
        stored_agents = self.memory_store.list_agents(
            agent_type.value if agent_type else None
        )
        
        for agent_data in stored_agents:
            agent_id = agent_data['agent_id']
            if agent_id not in self.registered_agents:
                agent = AgentInfo(
                    agent_id=agent_id,
                    agent_type=AgentType(agent_data['agent_type']),
                    name=agent_data['name'],
                    capabilities=agent_data['capabilities'],
                    status=agent_data['status'],
                    last_seen=datetime.fromisoformat(agent_data['last_seen']),
                    metadata=agent_data['metadata']
                )
                agents.append(agent)
        
        # Apply filters
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]
        if status:
            agents = [a for a in agents if a.status == status]
        
        return sorted(agents, key=lambda a: a.last_seen, reverse=True)
    
    def store_context(self, context_type: str, data: Dict[str, Any], 
                     metadata: Dict[str, Any] = None, expires_in_minutes: Optional[int] = None) -> ContextData:
        """Store context data"""
        expires_at = None
        if expires_in_minutes:
            expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
        
        context = ContextData(
            context_type=context_type,
            data=data,
            metadata=metadata or {},
            expires_at=expires_at
        )
        
        self.active_contexts[context.context_id] = context
        
        # Store in memory
        success = self.memory_store.store_context(context)
        
        if success:
            logger.info(f"Stored context {context.context_id} of type {context_type}")
        else:
            logger.error(f"Failed to store context {context.context_id}")
        
        return context
    
    def retrieve_context(self, context_id: str) -> Optional[ContextData]:
        """Retrieve context by ID"""
        # Check active contexts first
        if context_id in self.active_contexts:
            context = self.active_contexts[context_id]
            if not context.is_expired():
                return context
            else:
                # Remove expired context
                del self.active_contexts[context_id]
                self.memory_store.delete_context(context_id)
        
        # Try to load from memory store
        context = self.memory_store.retrieve_context(context_id)
        if context and not context.is_expired():
            self.active_contexts[context_id] = context
            return context
        
        return None
    
    def retrieve_contexts_by_type(self, context_type: str) -> List[ContextData]:
        """Retrieve all contexts of a specific type"""
        # Get from active contexts
        active_contexts = [
            ctx for ctx in self.active_contexts.values() 
            if ctx.context_type == context_type and not ctx.is_expired()
        ]
        
        # Get from memory store
        stored_contexts = self.memory_store.retrieve_contexts_by_type(context_type)
        
        # Combine and deduplicate
        all_contexts = {ctx.context_id: ctx for ctx in active_contexts}
        for ctx in stored_contexts:
            if ctx.context_id not in all_contexts:
                all_contexts[ctx.context_id] = ctx
                self.active_contexts[ctx.context_id] = ctx
        
        return sorted(all_contexts.values(), key=lambda c: c.created_at, reverse=True)
    
    def delete_context(self, context_id: str) -> bool:
        """Delete context"""
        # Remove from active contexts
        if context_id in self.active_contexts:
            del self.active_contexts[context_id]
        
        # Remove from memory store
        return self.memory_store.delete_context(context_id)
    
    def share_context_with_agent(self, context_id: str, agent_id: str) -> bool:
        """Share context with a specific agent"""
        context = self.retrieve_context(context_id)
        if not context:
            logger.error(f"Context {context_id} not found")
            return False
        
        agent = self.get_agent(agent_id)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return False
        
        # Add agent to context metadata
        if 'shared_with' not in context.metadata:
            context.metadata['shared_with'] = []
        
        if agent_id not in context.metadata['shared_with']:
            context.metadata['shared_with'].append(agent_id)
            context.metadata['last_shared'] = datetime.now().isoformat()
            
            # Update in memory store
            self.memory_store.store_context(context)
            
            logger.info(f"Shared context {context_id} with agent {agent_id}")
            return True
        
        return False
    
    def get_agent_contexts(self, agent_id: str) -> List[ContextData]:
        """Get all contexts shared with an agent"""
        contexts = []
        
        # Check all contexts for ones shared with this agent
        all_contexts = list(self.active_contexts.values())
        
        # Also get from memory store
        for context_type in ['general', 'conversation', 'system', 'agent_state']:
            stored_contexts = self.memory_store.retrieve_contexts_by_type(context_type)
            for ctx in stored_contexts:
                if ctx.context_id not in self.active_contexts:
                    all_contexts.append(ctx)
        
        for context in all_contexts:
            if not context.is_expired():
                shared_with = context.metadata.get('shared_with', [])
                if agent_id in shared_with:
                    contexts.append(context)
        
        return sorted(contexts, key=lambda c: c.created_at, reverse=True)
    
    def create_conversation_context(self, conversation_id: str, participants: List[str], 
                                  initial_data: Dict[str, Any] = None) -> ContextData:
        """Create context for a conversation"""
        data = {
            'conversation_id': conversation_id,
            'participants': participants,
            'created_at': datetime.now().isoformat(),
            **(initial_data or {})
        }
        
        metadata = {
            'conversation_id': conversation_id,
            'shared_with': participants.copy()
        }
        
        return self.store_context(
            context_type='conversation',
            data=data,
            metadata=metadata,
            expires_in_minutes=None  # Conversation contexts don't expire
        )
    
    def update_conversation_context(self, conversation_id: str, data_updates: Dict[str, Any]) -> bool:
        """Update conversation context"""
        # Find conversation context
        conversation_contexts = self.retrieve_contexts_by_type('conversation')
        for context in conversation_contexts:
            if context.data.get('conversation_id') == conversation_id:
                # Update data
                context.data.update(data_updates)
                context.metadata['last_updated'] = datetime.now().isoformat()
                
                # Store updated context
                self.memory_store.store_context(context)
                return True
        
        return False
    
    def cleanup_expired_contexts(self) -> int:
        """Clean up expired contexts"""
        # Clean from active contexts
        expired_ids = [
            ctx_id for ctx_id, ctx in self.active_contexts.items()
            if ctx.is_expired()
        ]
        
        for ctx_id in expired_ids:
            del self.active_contexts[ctx_id]
        
        # Clean from memory store
        cleaned_count = self.memory_store.cleanup_expired_contexts()
        
        total_cleaned = len(expired_ids) + cleaned_count
        if total_cleaned > 0:
            logger.info(f"Cleaned up {total_cleaned} expired contexts")
        
        return total_cleaned
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get context manager statistics"""
        stats = {
            'active_contexts': len(self.active_contexts),
            'registered_agents': len(self.registered_agents),
            'agent_types': {}
        }
        
        # Count agents by type
        for agent in self.registered_agents.values():
            agent_type = agent.agent_type.value
            stats['agent_types'][agent_type] = stats['agent_types'].get(agent_type, 0) + 1
        
        # Add memory store statistics
        memory_stats = self.memory_store.get_statistics()
        stats.update(memory_stats)
        
        return stats