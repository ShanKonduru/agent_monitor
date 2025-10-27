"""
Model Context Protocol (MCP) Server
Main server for managing AI model context sharing and agent communication
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import uuid
from dataclasses import asdict

from .protocol import (
    MCPMessage, MCPRequest, MCPResponse, MessageType, AgentType, 
    ContextData, AgentInfo
)
from .context_manager import ContextManager
from .conversation import ConversationManager, Conversation
from .memory_store import MemoryStore

logger = logging.getLogger(__name__)

class MCPServer:
    """Model Context Protocol Server"""
    
    def __init__(self, memory_db_path: str = "data/mcp_memory.db"):
        """Initialize MCP server"""
        self.memory_store = MemoryStore(memory_db_path)
        self.context_manager = ContextManager(self.memory_store)
        self.conversation_manager = ConversationManager(self.memory_store)
        
        # Message handlers
        self.message_handlers: Dict[MessageType, Callable] = {
            MessageType.CONTEXT_SHARE: self._handle_context_share,
            MessageType.CONVERSATION_START: self._handle_conversation_start,
            MessageType.CONVERSATION_MESSAGE: self._handle_conversation_message,
            MessageType.CONVERSATION_END: self._handle_conversation_end,
            MessageType.MEMORY_STORE: self._handle_memory_store,
            MessageType.MEMORY_RETRIEVE: self._handle_memory_retrieve,
            MessageType.AGENT_REGISTER: self._handle_agent_register,
            MessageType.AGENT_STATUS: self._handle_agent_status,
            MessageType.SYSTEM_BROADCAST: self._handle_system_broadcast
        }
        
        # Connected clients (for future WebSocket support)
        self.connected_clients: Dict[str, Any] = {}
        
        logger.info("MCPServer initialized")
    
    async def start(self):
        """Start the MCP server"""
        logger.info("🚀 MCP Server starting...")
        
        # Perform startup tasks
        await self._startup_tasks()
        
        logger.info("✅ MCP Server ready!")
    
    async def stop(self):
        """Stop the MCP server"""
        logger.info("🛑 MCP Server stopping...")
        
        # Perform cleanup tasks
        await self._cleanup_tasks()
        
        logger.info("✅ MCP Server stopped")
    
    async def _startup_tasks(self):
        """Perform startup initialization"""
        # Register the MCP server itself as an agent
        self.context_manager.register_agent(
            agent_id="mcp_server",
            agent_type=AgentType.MONITOR_AGENT,
            name="MCP Server",
            capabilities=["context_management", "conversation_threading", "memory_storage"],
            metadata={"version": "1.0.0", "started_at": datetime.now().isoformat()}
        )
        
        # Clean up expired contexts
        self.context_manager.cleanup_expired_contexts()
        
        logger.info("Startup tasks completed")
    
    async def _cleanup_tasks(self):
        """Perform cleanup on shutdown"""
        # Update server status
        self.context_manager.update_agent_status(
            "mcp_server", 
            "stopped", 
            {"stopped_at": datetime.now().isoformat()}
        )
        
        logger.info("Cleanup tasks completed")
    
    async def process_message(self, message_data: Dict[str, Any]) -> Optional[MCPResponse]:
        """Process incoming MCP message"""
        try:
            # Parse message
            message = MCPMessage.from_dict(message_data)
            
            logger.debug(f"Processing message {message.id} of type {message.type.value}")
            
            # Get handler for message type
            handler = self.message_handlers.get(message.type)
            if not handler:
                logger.warning(f"No handler for message type {message.type.value}")
                return MCPResponse(
                    sender_id="mcp_server",
                    sender_type=AgentType.MONITOR_AGENT,
                    request_id=getattr(message, 'request_id', message.id),
                    success=False,
                    error_message=f"Unknown message type: {message.type.value}"
                )
            
            # Process message
            response = await handler(message)
            
            # Store message in conversation if applicable
            if message.conversation_id:
                self.conversation_manager.add_message_to_conversation(message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                success=False,
                error_message=str(e)
            )
    
    async def _handle_context_share(self, message: MCPMessage) -> MCPResponse:
        """Handle context sharing request"""
        try:
            payload = message.payload
            context_type = payload.get('context_type', 'general')
            data = payload.get('data', {})
            metadata = payload.get('metadata', {})
            expires_in_minutes = payload.get('expires_in_minutes')
            
            # Store context
            context = self.context_manager.store_context(
                context_type=context_type,
                data=data,
                metadata=metadata,
                expires_in_minutes=expires_in_minutes
            )
            
            # Share with recipient if specified
            if message.recipient_id:
                self.context_manager.share_context_with_agent(
                    context.context_id,
                    message.recipient_id
                )
            
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                recipient_id=message.sender_id,
                request_id=getattr(message, 'request_id', message.id),
                success=True,
                response_data={
                    'context_id': context.context_id,
                    'message': 'Context shared successfully'
                }
            )
            
        except Exception as e:
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                request_id=getattr(message, 'request_id', message.id),
                success=False,
                error_message=str(e)
            )
    
    async def _handle_conversation_start(self, message: MCPMessage) -> MCPResponse:
        """Handle conversation start request"""
        try:
            payload = message.payload
            title = payload.get('title', f"Conversation started by {message.sender_id}")
            participants = payload.get('participants', [message.sender_id])
            metadata = payload.get('metadata', {})
            
            # Create conversation
            conversation = self.conversation_manager.create_conversation(
                title=title,
                participants=participants,
                metadata=metadata
            )
            
            # Create conversation context
            self.context_manager.create_conversation_context(
                conversation.conversation_id,
                participants,
                {'title': title, 'started_by': message.sender_id}
            )
            
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                recipient_id=message.sender_id,
                request_id=getattr(message, 'request_id', message.id),
                success=True,
                response_data={
                    'conversation_id': conversation.conversation_id,
                    'message': 'Conversation started successfully'
                }
            )
            
        except Exception as e:
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                request_id=getattr(message, 'request_id', message.id),
                success=False,
                error_message=str(e)
            )
    
    async def _handle_conversation_message(self, message: MCPMessage) -> MCPResponse:
        """Handle conversation message"""
        try:
            # Message is automatically stored by process_message
            # Update conversation context with message info
            if message.conversation_id:
                self.context_manager.update_conversation_context(
                    message.conversation_id,
                    {
                        'last_message_at': message.timestamp.isoformat(),
                        'last_message_from': message.sender_id
                    }
                )
            
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                recipient_id=message.sender_id,
                request_id=getattr(message, 'request_id', message.id),
                success=True,
                response_data={'message': 'Message processed successfully'}
            )
            
        except Exception as e:
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                request_id=getattr(message, 'request_id', message.id),
                success=False,
                error_message=str(e)
            )
    
    async def _handle_conversation_end(self, message: MCPMessage) -> MCPResponse:
        """Handle conversation end request"""
        try:
            conversation_id = message.payload.get('conversation_id', message.conversation_id)
            
            if conversation_id:
                # Archive conversation
                success = self.conversation_manager.archive_conversation(conversation_id)
                
                if success:
                    # Update conversation context
                    self.context_manager.update_conversation_context(
                        conversation_id,
                        {
                            'ended_at': message.timestamp.isoformat(),
                            'ended_by': message.sender_id
                        }
                    )
                
                return MCPResponse(
                    sender_id="mcp_server",
                    sender_type=AgentType.MONITOR_AGENT,
                    recipient_id=message.sender_id,
                    request_id=getattr(message, 'request_id', message.id),
                    success=success,
                    response_data={'message': 'Conversation ended successfully' if success else 'Conversation not found'}
                )
            else:
                return MCPResponse(
                    sender_id="mcp_server",
                    sender_type=AgentType.MONITOR_AGENT,
                    request_id=getattr(message, 'request_id', message.id),
                    success=False,
                    error_message="No conversation_id provided"
                )
                
        except Exception as e:
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                request_id=getattr(message, 'request_id', message.id),
                success=False,
                error_message=str(e)
            )
    
    async def _handle_memory_store(self, message: MCPMessage) -> MCPResponse:
        """Handle memory storage request"""
        try:
            payload = message.payload
            memory_type = payload.get('memory_type', 'general')
            data = payload.get('data', {})
            metadata = payload.get('metadata', {})
            
            # Store as context
            context = self.context_manager.store_context(
                context_type=memory_type,
                data=data,
                metadata=metadata
            )
            
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                recipient_id=message.sender_id,
                request_id=getattr(message, 'request_id', message.id),
                success=True,
                response_data={
                    'context_id': context.context_id,
                    'message': 'Memory stored successfully'
                }
            )
            
        except Exception as e:
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                request_id=getattr(message, 'request_id', message.id),
                success=False,
                error_message=str(e)
            )
    
    async def _handle_memory_retrieve(self, message: MCPMessage) -> MCPResponse:
        """Handle memory retrieval request"""
        try:
            payload = message.payload
            context_id = payload.get('context_id')
            memory_type = payload.get('memory_type')
            
            if context_id:
                # Retrieve specific context
                context = self.context_manager.retrieve_context(context_id)
                if context:
                    return MCPResponse(
                        sender_id="mcp_server",
                        sender_type=AgentType.MONITOR_AGENT,
                        recipient_id=message.sender_id,
                        request_id=getattr(message, 'request_id', message.id),
                        success=True,
                        response_data={
                            'context': {
                                'context_id': context.context_id,
                                'context_type': context.context_type,
                                'data': context.data,
                                'metadata': context.metadata,
                                'created_at': context.created_at.isoformat()
                            }
                        }
                    )
                else:
                    return MCPResponse(
                        sender_id="mcp_server",
                        sender_type=AgentType.MONITOR_AGENT,
                        request_id=getattr(message, 'request_id', message.id),
                        success=False,
                        error_message="Context not found"
                    )
            
            elif memory_type:
                # Retrieve all contexts of type
                contexts = self.context_manager.retrieve_contexts_by_type(memory_type)
                return MCPResponse(
                    sender_id="mcp_server",
                    sender_type=AgentType.MONITOR_AGENT,
                    recipient_id=message.sender_id,
                    request_id=getattr(message, 'request_id', message.id),
                    success=True,
                    response_data={
                        'contexts': [
                            {
                                'context_id': ctx.context_id,
                                'context_type': ctx.context_type,
                                'data': ctx.data,
                                'metadata': ctx.metadata,
                                'created_at': ctx.created_at.isoformat()
                            } for ctx in contexts
                        ]
                    }
                )
            
            else:
                return MCPResponse(
                    sender_id="mcp_server",
                    sender_type=AgentType.MONITOR_AGENT,
                    request_id=getattr(message, 'request_id', message.id),
                    success=False,
                    error_message="Must provide either context_id or memory_type"
                )
                
        except Exception as e:
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                request_id=getattr(message, 'request_id', message.id),
                success=False,
                error_message=str(e)
            )
    
    async def _handle_agent_register(self, message: MCPMessage) -> MCPResponse:
        """Handle agent registration request"""
        try:
            payload = message.payload
            agent_type = AgentType(payload.get('agent_type', 'external_client'))
            name = payload.get('name', f"Agent {message.sender_id}")
            capabilities = payload.get('capabilities', [])
            metadata = payload.get('metadata', {})
            
            # Register agent
            success = self.context_manager.register_agent(
                agent_id=message.sender_id,
                agent_type=agent_type,
                name=name,
                capabilities=capabilities,
                metadata=metadata
            )
            
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                recipient_id=message.sender_id,
                request_id=getattr(message, 'request_id', message.id),
                success=success,
                response_data={'message': 'Agent registered successfully' if success else 'Registration failed'}
            )
            
        except Exception as e:
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                request_id=getattr(message, 'request_id', message.id),
                success=False,
                error_message=str(e)
            )
    
    async def _handle_agent_status(self, message: MCPMessage) -> MCPResponse:
        """Handle agent status update"""
        try:
            payload = message.payload
            status = payload.get('status', 'active')
            metadata = payload.get('metadata', {})
            
            # Update agent status
            success = self.context_manager.update_agent_status(
                message.sender_id,
                status,
                metadata
            )
            
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                recipient_id=message.sender_id,
                request_id=getattr(message, 'request_id', message.id),
                success=success,
                response_data={'message': 'Status updated successfully' if success else 'Update failed'}
            )
            
        except Exception as e:
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                request_id=getattr(message, 'request_id', message.id),
                success=False,
                error_message=str(e)
            )
    
    async def _handle_system_broadcast(self, message: MCPMessage) -> MCPResponse:
        """Handle system broadcast message"""
        try:
            # For now, just acknowledge the broadcast
            # In future, could implement actual broadcasting to connected clients
            
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                recipient_id=message.sender_id,
                request_id=getattr(message, 'request_id', message.id),
                success=True,
                response_data={'message': 'Broadcast received'}
            )
            
        except Exception as e:
            return MCPResponse(
                sender_id="mcp_server",
                sender_type=AgentType.MONITOR_AGENT,
                request_id=getattr(message, 'request_id', message.id),
                success=False,
                error_message=str(e)
            )
    
    # Public API methods
    
    def get_conversations(self, participant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get conversations"""
        conversations = self.conversation_manager.list_conversations(participant_id)
        return [conv.to_dict() for conv in conversations]
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get specific conversation"""
        conversation = self.conversation_manager.get_conversation(conversation_id)
        if conversation:
            return conversation.to_dict()
        return None
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get conversation messages"""
        return self.conversation_manager.get_conversation_messages(conversation_id, limit)
    
    def get_agents(self, agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get registered agents"""
        agent_type_enum = AgentType(agent_type) if agent_type else None
        agents = self.context_manager.list_agents(agent_type_enum)
        return [agent.to_dict() for agent in agents]
    
    def get_contexts(self, context_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get contexts"""
        if context_type:
            contexts = self.context_manager.retrieve_contexts_by_type(context_type)
        else:
            # Get all context types
            contexts = []
            for ctx_type in ['general', 'conversation', 'system', 'agent_state']:
                contexts.extend(self.context_manager.retrieve_contexts_by_type(ctx_type))
        
        return [
            {
                'context_id': ctx.context_id,
                'context_type': ctx.context_type,
                'data': ctx.data,
                'metadata': ctx.metadata,
                'created_at': ctx.created_at.isoformat(),
                'expires_at': ctx.expires_at.isoformat() if ctx.expires_at else None
            } for ctx in contexts
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get server statistics"""
        context_stats = self.context_manager.get_statistics()
        conversation_stats = self.conversation_manager.get_statistics()
        
        return {
            'server_info': {
                'version': '1.0.0',
                'uptime': datetime.now().isoformat(),
                'connected_clients': len(self.connected_clients)
            },
            'contexts': context_stats,
            'conversations': conversation_stats
        }