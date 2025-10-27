"""
Chatbot Core System
Main chatbot engine integrating AI providers, MCP server, and command processing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .chat_session import ChatSessionManager, ChatSession, ChatMessage, MessageType, MessageStatus
from .chat_commands import CommandProcessor
from .integrations import AIProviderIntegration, MCPIntegration

logger = logging.getLogger(__name__)

class ChatbotCore:
    """Core chatbot system"""
    
    def __init__(self, ai_provider_manager=None, mcp_server=None):
        """Initialize chatbot core"""
        # Core components
        self.session_manager = ChatSessionManager()
        self.command_processor = CommandProcessor()
        
        # Integrations
        self.ai_integration = AIProviderIntegration(ai_provider_manager)
        self.mcp_integration = MCPIntegration(mcp_server)
        
        # Configuration
        self.default_ai_provider = "local"
        self.default_ai_model = "llama3.1"
        self.default_temperature = 0.7
        self.default_max_tokens = 1000
        
        # System prompts
        self.system_prompts = {
            "default": """You are an AI assistant for the Agent Monitor system. You help users manage and monitor their agent infrastructure.

You have access to:
- AI provider management (OpenAI, Anthropic, Local LLM)
- System monitoring and statistics
- Agent communication and coordination
- Context sharing between agents

Be helpful, informative, and concise. If users need specific system information, suggest relevant commands (starting with /).

Available commands: /help, /status, /providers, /models, /stats, and more.""",
            
            "technical": """You are a technical AI assistant for the Agent Monitor system. You provide detailed technical information about:

- AI provider configurations and performance
- MCP (Model Context Protocol) operations
- System architecture and troubleshooting
- Agent communication patterns
- Performance optimization

Provide precise, technical responses with specific metrics when available.""",
            
            "friendly": """You are a friendly AI assistant helping with the Agent Monitor system. You make complex technical concepts easy to understand and provide a welcoming experience.

You help users:
- Get started with the system
- Understand AI provider options
- Navigate system features
- Troubleshoot issues in a supportive way

Keep responses conversational and encouraging while being informative."""
        }
        
        logger.info("ChatbotCore initialized")
    
    async def create_chat_session(self, user_id: str = "anonymous", title: str = "New Chat",
                                ai_provider: Optional[str] = None, ai_model: Optional[str] = None,
                                system_prompt: str = "default", **kwargs) -> ChatSession:
        """Create a new chat session"""
        # Use defaults if not specified
        ai_provider = ai_provider or self.default_ai_provider
        ai_model = ai_model or self.default_ai_model
        
        # Create session
        session = self.session_manager.create_session(
            user_id=user_id,
            title=title,
            ai_provider=ai_provider,
            ai_model=ai_model,
            temperature=kwargs.get('temperature', self.default_temperature),
            max_tokens=kwargs.get('max_tokens', self.default_max_tokens)
        )
        
        # Set system prompt in context
        session.context['system_prompt'] = system_prompt
        session.context['system_prompt_text'] = self.system_prompts.get(system_prompt, self.system_prompts['default'])
        
        # Create MCP conversation if available
        if self.mcp_integration.mcp_server:
            conversation_id = await self.mcp_integration.create_conversation(
                title=title,
                participants=["chatbot", user_id]
            )
            session.mcp_conversation_id = conversation_id
        
        # Add system message
        session.add_message(
            MessageType.SYSTEM,
            session.context['system_prompt_text'],
            {"system_prompt": system_prompt}
        )
        
        logger.info(f"Created chat session {session.session_id} for user {user_id}")
        return session
    
    async def process_message(self, session_id: str, user_message: str, 
                            metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a user message and generate response"""
        try:
            # Get session
            session = self.session_manager.get_session(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found",
                    "session_id": session_id
                }
            
            # Add user message to session
            user_msg = session.add_message(
                MessageType.USER,
                user_message,
                metadata or {}
            )
            
            # Check if it's a command
            if self.command_processor.is_command(user_message):
                return await self._process_command(session, user_message)
            else:
                return await self._process_chat_message(session, user_message)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def _process_command(self, session: ChatSession, command_text: str) -> Dict[str, Any]:
        """Process a chat command"""
        try:
            # Prepare context for command processor
            context = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "ai_provider": session.ai_provider,
                "ai_model": session.ai_model,
                "temperature": session.temperature,
                "is_admin": False,  # TODO: Implement admin detection
                "debug_mode": session.context.get("debug_mode", False),
                "ai_integration": self.ai_integration,
                "mcp_integration": self.mcp_integration,
                "session": session
            }
            
            # Process command
            result = await self.command_processor.process_command(command_text, context)
            
            # Add command message to session
            cmd_msg = session.add_message(
                MessageType.COMMAND,
                command_text,
                {"command_result": result}
            )
            cmd_msg.status = MessageStatus.COMPLETED if result["success"] else MessageStatus.FAILED
            
            # Add response message
            response_type = MessageType.INFO if result["success"] else MessageType.ERROR
            response_msg = session.add_message(
                response_type,
                result["response"],
                {"command": result.get("command"), "original_command": command_text}
            )
            
            # Add to MCP conversation if available
            if session.mcp_conversation_id:
                await self.mcp_integration.add_message_to_conversation(
                    session.mcp_conversation_id,
                    f"Command: {command_text}\nResult: {result['response']}",
                    session.user_id
                )
            
            return {
                "success": True,
                "session_id": session.session_id,
                "message_id": response_msg.id,
                "response": result["response"],
                "type": "command",
                "command": result.get("command"),
                "metadata": {
                    "command_success": result["success"],
                    "command_error": result.get("error")
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            
            # Add error message
            error_msg = session.add_message(
                MessageType.ERROR,
                f"Command error: {e}",
                {"error": str(e), "command": command_text}
            )
            
            return {
                "success": False,
                "session_id": session.session_id,
                "message_id": error_msg.id,
                "error": str(e),
                "type": "command_error"
            }
    
    async def _process_chat_message(self, session: ChatSession, user_message: str) -> Dict[str, Any]:
        """Process a regular chat message"""
        try:
            # Create assistant message placeholder
            assistant_msg = session.add_message(
                MessageType.ASSISTANT,
                "",  # Will be filled with response
                {"processing": True}
            )
            assistant_msg.status = MessageStatus.PROCESSING
            
            # Prepare conversation history
            history = session.get_conversation_history(limit=20)
            
            # Add system prompt if not in history
            if not any(msg.get("role") == "system" for msg in history):
                system_prompt = session.context.get('system_prompt_text', self.system_prompts['default'])
                history.insert(0, {"role": "system", "content": system_prompt})
            
            # Add current user message
            history.append({"role": "user", "content": user_message})
            
            # Get AI completion
            start_time = datetime.now()
            
            completion_result = await self.ai_integration.complete(
                prompt=user_message,  # For simple providers
                messages=history,     # For chat-based providers
                temperature=session.temperature,
                max_tokens=session.max_tokens
            )
            
            end_time = datetime.now()
            latency_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Update assistant message with response
            assistant_msg.content = completion_result["content"]
            assistant_msg.status = MessageStatus.COMPLETED
            assistant_msg.provider = completion_result.get("provider")
            assistant_msg.model = completion_result.get("model")
            assistant_msg.tokens_used = completion_result.get("tokens_used", 0)
            assistant_msg.latency_ms = completion_result.get("latency_ms", latency_ms)
            assistant_msg.cost = completion_result.get("cost", 0.0)
            assistant_msg.metadata.pop("processing", None)
            
            # Update session timestamp
            session.update_timestamp()
            
            # Add to MCP conversation if available
            if session.mcp_conversation_id:
                await self.mcp_integration.add_message_to_conversation(
                    session.mcp_conversation_id,
                    f"User: {user_message}\nAssistant: {assistant_msg.content}",
                    session.user_id
                )
            
            return {
                "success": True,
                "session_id": session.session_id,
                "message_id": assistant_msg.id,
                "response": assistant_msg.content,
                "type": "chat",
                "metadata": {
                    "provider": assistant_msg.provider,
                    "model": assistant_msg.model,
                    "tokens_used": assistant_msg.tokens_used,
                    "latency_ms": assistant_msg.latency_ms,
                    "cost": assistant_msg.cost
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            
            # Update assistant message with error
            assistant_msg.content = f"I'm sorry, I encountered an error: {e}"
            assistant_msg.status = MessageStatus.FAILED
            assistant_msg.metadata["error"] = str(e)
            
            return {
                "success": False,
                "session_id": session.session_id,
                "message_id": assistant_msg.id,
                "error": str(e),
                "type": "chat_error"
            }
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID"""
        return self.session_manager.get_session(session_id)
    
    def list_sessions(self, user_id: Optional[str] = None) -> List[ChatSession]:
        """List chat sessions"""
        return self.session_manager.list_sessions(user_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete chat session"""
        return self.session_manager.delete_session(session_id)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Get AI provider status
            ai_health = await self.ai_integration.get_provider_health()
            ai_stats = await self.ai_integration.get_provider_stats()
            
            # Get MCP status
            mcp_stats = await self.mcp_integration.get_mcp_statistics()
            
            # Get session statistics
            session_stats = self.session_manager.get_statistics()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "chatbot": {
                    "status": "operational",
                    "sessions": session_stats
                },
                "ai_providers": {
                    "health": ai_health,
                    "statistics": ai_stats
                },
                "mcp": {
                    "statistics": mcp_stats
                }
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }
    
    async def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up old inactive sessions"""
        # This would implement session cleanup logic
        # For now, return 0 as placeholder
        return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get chatbot statistics"""
        return {
            "chatbot_core": {
                "version": "1.0.0",
                "default_provider": self.default_ai_provider,
                "default_model": self.default_ai_model,
                "system_prompts": list(self.system_prompts.keys()),
                "available_commands": len(self.command_processor.commands)
            },
            "sessions": self.session_manager.get_statistics()
        }