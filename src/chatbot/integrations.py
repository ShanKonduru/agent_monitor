"""
Integration modules for chatbot system
Connects chatbot with AI providers and MCP server
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AIProviderIntegration:
    """Integration with Phase 6.1 AI Provider system"""
    
    def __init__(self, provider_manager=None):
        """Initialize AI provider integration"""
        self.provider_manager = provider_manager
        self.current_provider = "local"
        self.current_model = "llama3.1"
        logger.info("AIProviderIntegration initialized")
    
    async def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        if self.provider_manager:
            return list(self.provider_manager.providers.keys())
        return ["local", "openai", "anthropic"]
    
    async def get_available_models(self, provider: Optional[str] = None) -> List[str]:
        """Get available models for a provider"""
        target_provider = provider or self.current_provider
        
        if self.provider_manager and target_provider in self.provider_manager.providers:
            try:
                provider_instance = self.provider_manager.providers[target_provider]
                models = await provider_instance.get_models()
                return [model.name for model in models]
            except Exception as e:
                logger.error(f"Error getting models for {target_provider}: {e}")
                return []
        
        # Fallback mock data
        mock_models = {
            "local": ["llama3.1", "llama2", "qwen3-coder", "codellama"],
            "openai": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
            "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
        }
        return mock_models.get(target_provider, [])
    
    async def switch_provider(self, provider: str) -> bool:
        """Switch to a different AI provider"""
        try:
            if self.provider_manager:
                success = await self.provider_manager.switch_provider(provider)
                if success:
                    self.current_provider = provider
                    logger.info(f"Switched to provider: {provider}")
                    return True
            else:
                # Mock mode for testing
                available_providers = await self.get_available_providers()
                if provider in available_providers:
                    self.current_provider = provider
                    logger.info(f"Mock switched to provider: {provider}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error switching provider to {provider}: {e}")
            return False
    
    async def switch_model(self, model: str) -> bool:
        """Switch to a different AI model"""
        try:
            if self.provider_manager:
                current_provider_instance = self.provider_manager.get_current_provider()
                if current_provider_instance:
                    success = await current_provider_instance.switch_model(model)
                    if success:
                        self.current_model = model
                        logger.info(f"Switched to model: {model}")
                        return True
            else:
                # Mock mode for testing
                available_models = await self.get_available_models()
                if model in available_models:
                    self.current_model = model
                    logger.info(f"Mock switched to model: {model}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error switching model to {model}: {e}")
            return False
    
    async def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Get completion from AI provider"""
        try:
            if self.provider_manager:
                # Use real provider manager
                result = await self.provider_manager.complete(
                    prompt=prompt,
                    **kwargs
                )
                return {
                    "content": result.content,
                    "provider": result.provider,
                    "model": result.model,
                    "tokens_used": result.tokens_used,
                    "latency_ms": result.latency_ms,
                    "cost": result.cost
                }
            else:
                # Mock response for testing
                import time
                start_time = time.time()
                
                # Simulate processing delay
                await asyncio.sleep(0.5)
                
                latency = int((time.time() - start_time) * 1000)
                
                return {
                    "content": f"Mock response from {self.current_provider}/{self.current_model}: {prompt[:50]}...",
                    "provider": self.current_provider,
                    "model": self.current_model,
                    "tokens_used": len(prompt.split()) + 20,
                    "latency_ms": latency,
                    "cost": 0.0
                }
        except Exception as e:
            logger.error(f"Error getting completion: {e}")
            raise
    
    async def get_provider_health(self) -> Dict[str, bool]:
        """Get health status of all providers"""
        if self.provider_manager:
            return await self.provider_manager.health_check()
        
        # Mock health status
        return {
            "local": True,
            "openai": False,
            "anthropic": False
        }
    
    async def get_provider_stats(self) -> Dict[str, Any]:
        """Get provider statistics"""
        if self.provider_manager:
            return self.provider_manager.get_statistics()
        
        # Mock statistics
        return {
            "total_requests": 42,
            "successful_requests": 40,
            "failed_requests": 2,
            "total_tokens": 15432,
            "total_cost": 2.45,
            "avg_latency_ms": 1247,
            "success_rate": 95.2
        }

class MCPIntegration:
    """Integration with Phase 6.2 MCP server"""
    
    def __init__(self, mcp_server=None):
        """Initialize MCP integration"""
        self.mcp_server = mcp_server
        logger.info("MCPIntegration initialized")
    
    async def create_conversation(self, title: str, participants: List[str]) -> Optional[str]:
        """Create a new MCP conversation"""
        try:
            if self.mcp_server:
                # Use real MCP server
                from ..mcp.protocol import MCPRequest, MessageType, AgentType
                
                message = MCPRequest(
                    type=MessageType.CONVERSATION_START,
                    sender_id="chatbot",
                    sender_type=AgentType.CHATBOT,
                    payload={
                        "title": title,
                        "participants": participants,
                        "metadata": {"created_by": "chatbot"}
                    }
                )
                
                response = await self.mcp_server.process_message(message.to_dict())
                if response and response.success:
                    conversation_id = response.response_data.get("conversation_id")
                    logger.info(f"Created MCP conversation: {conversation_id}")
                    return conversation_id
            else:
                # Mock conversation ID
                import uuid
                conversation_id = str(uuid.uuid4())
                logger.info(f"Mock created conversation: {conversation_id}")
                return conversation_id
            
            return None
        except Exception as e:
            logger.error(f"Error creating MCP conversation: {e}")
            return None
    
    async def add_message_to_conversation(self, conversation_id: str, message_content: str, 
                                        sender_id: str = "chatbot") -> bool:
        """Add message to MCP conversation"""
        try:
            if self.mcp_server:
                from ..mcp.protocol import MCPMessage, MessageType, AgentType
                
                message = MCPMessage(
                    type=MessageType.CONVERSATION_MESSAGE,
                    sender_id=sender_id,
                    sender_type=AgentType.CHATBOT,
                    conversation_id=conversation_id,
                    payload={
                        "content": message_content,
                        "message_type": "text",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                response = await self.mcp_server.process_message(message.to_dict())
                return response and response.success
            else:
                # Mock success
                logger.info(f"Mock added message to conversation {conversation_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding message to MCP conversation: {e}")
            return False
    
    async def share_context(self, context_type: str, data: Dict[str, Any], 
                          recipient: Optional[str] = None) -> Optional[str]:
        """Share context with MCP"""
        try:
            if self.mcp_server:
                from ..mcp.protocol import MCPRequest, MessageType, AgentType
                
                message = MCPRequest(
                    type=MessageType.CONTEXT_SHARE,
                    sender_id="chatbot",
                    sender_type=AgentType.CHATBOT,
                    recipient_id=recipient,
                    payload={
                        "context_type": context_type,
                        "data": data,
                        "metadata": {"shared_by": "chatbot"},
                        "expires_in_minutes": 60  # 1 hour default
                    }
                )
                
                response = await self.mcp_server.process_message(message.to_dict())
                if response and response.success:
                    context_id = response.response_data.get("context_id")
                    logger.info(f"Shared context with MCP: {context_id}")
                    return context_id
            else:
                # Mock context ID
                import uuid
                context_id = str(uuid.uuid4())
                logger.info(f"Mock shared context: {context_id}")
                return context_id
            
            return None
        except Exception as e:
            logger.error(f"Error sharing context with MCP: {e}")
            return None
    
    async def retrieve_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve context from MCP"""
        try:
            if self.mcp_server:
                from ..mcp.protocol import MCPRequest, MessageType, AgentType
                
                message = MCPRequest(
                    type=MessageType.MEMORY_RETRIEVE,
                    sender_id="chatbot",
                    sender_type=AgentType.CHATBOT,
                    payload={"context_id": context_id}
                )
                
                response = await self.mcp_server.process_message(message.to_dict())
                if response and response.success:
                    return response.response_data.get("context")
            else:
                # Mock context data
                return {
                    "context_id": context_id,
                    "context_type": "general",
                    "data": {"mock": "context data"},
                    "metadata": {},
                    "created_at": datetime.now().isoformat()
                }
            
            return None
        except Exception as e:
            logger.error(f"Error retrieving context from MCP: {e}")
            return None
    
    async def get_conversations(self) -> List[Dict[str, Any]]:
        """Get conversations from MCP"""
        try:
            if self.mcp_server:
                return self.mcp_server.get_conversations("chatbot")
            else:
                # Mock conversations
                return [
                    {
                        "conversation_id": "conv-1",
                        "title": "Mock Conversation 1",
                        "participants": ["chatbot", "user"],
                        "status": "active"
                    }
                ]
        except Exception as e:
            logger.error(f"Error getting conversations from MCP: {e}")
            return []
    
    async def get_mcp_statistics(self) -> Dict[str, Any]:
        """Get MCP server statistics"""
        try:
            if self.mcp_server:
                return self.mcp_server.get_statistics()
            else:
                # Mock statistics
                return {
                    "total_conversations": 5,
                    "active_conversations": 2,
                    "total_contexts": 15,
                    "total_agents": 3
                }
        except Exception as e:
            logger.error(f"Error getting MCP statistics: {e}")
            return {}

# Import asyncio for mock mode
import asyncio