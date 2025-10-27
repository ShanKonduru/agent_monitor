"""
FastAPI Router for Chatbot System
Provides REST API endpoints for chatbot functionality
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

from ..chatbot.chatbot_core import ChatbotCore
from ..ai_providers.provider_manager import AIProviderManager
from ..mcp.mcp_server import MCPServer

logger = logging.getLogger(__name__)

# Pydantic models for API requests
class CreateSessionRequest(BaseModel):
    user_id: str = "anonymous"
    title: str = "New Chat"
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    system_prompt: str = "default"
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class SendMessageRequest(BaseModel):
    message: str
    metadata: Optional[Dict[str, Any]] = None

class UpdateSessionRequest(BaseModel):
    title: Optional[str] = None
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

# Global chatbot instance
chatbot_core: Optional[ChatbotCore] = None

def get_chatbot_core() -> ChatbotCore:
    """Get the chatbot core instance"""
    global chatbot_core
    if chatbot_core is None:
        # Initialize chatbot with available components
        # In production, these would be properly injected
        try:
            # Try to get AI provider manager
            from ..ai_providers.provider_manager import get_provider_manager
            ai_provider_manager = get_provider_manager()
        except:
            ai_provider_manager = None
            logger.warning("AI Provider Manager not available")
        
        try:
            # Try to get MCP server
            from ..api.mcp_router import get_mcp_server
            mcp_server = get_mcp_server()
        except:
            mcp_server = None
            logger.warning("MCP Server not available")
        
        chatbot_core = ChatbotCore(
            ai_provider_manager=ai_provider_manager,
            mcp_server=mcp_server
        )
        logger.info("ChatbotCore initialized for API")
    
    return chatbot_core

# Create router
router = APIRouter(prefix="/api/v1/chat", tags=["Chatbot"])

@router.get("/status")
async def get_chatbot_status():
    """Get chatbot status"""
    chatbot = get_chatbot_core()
    try:
        status = await chatbot.get_system_status()
        return {
            "status": "operational",
            "message": "Chatbot system is running",
            "details": status
        }
    except Exception as e:
        logger.error(f"Error getting chatbot status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_chatbot_statistics():
    """Get chatbot statistics"""
    chatbot = get_chatbot_core()
    try:
        return chatbot.get_statistics()
    except Exception as e:
        logger.error(f"Error getting chatbot statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Session Management Endpoints

@router.post("/sessions")
async def create_session(request: CreateSessionRequest):
    """Create a new chat session"""
    chatbot = get_chatbot_core()
    try:
        session = await chatbot.create_chat_session(
            user_id=request.user_id,
            title=request.title,
            ai_provider=request.ai_provider,
            ai_model=request.ai_model,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return {
            "success": True,
            "session": session.to_dict()
        }
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def list_sessions(user_id: Optional[str] = None):
    """List chat sessions"""
    chatbot = get_chatbot_core()
    try:
        sessions = chatbot.list_sessions(user_id)
        return {
            "success": True,
            "sessions": [session.to_dict() for session in sessions],
            "count": len(sessions)
        }
    except Exception as e:
        logger.error(f"Error listing chat sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get specific chat session"""
    chatbot = get_chatbot_core()
    try:
        session = chatbot.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session": session.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sessions/{session_id}")
async def update_session(session_id: str, request: UpdateSessionRequest):
    """Update chat session settings"""
    chatbot = get_chatbot_core()
    try:
        session = chatbot.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update session properties
        if request.title is not None:
            session.title = request.title
        if request.ai_provider is not None:
            session.ai_provider = request.ai_provider
        if request.ai_model is not None:
            session.ai_model = request.ai_model
        if request.temperature is not None:
            session.temperature = request.temperature
        if request.max_tokens is not None:
            session.max_tokens = request.max_tokens
        
        session.update_timestamp()
        
        return {
            "success": True,
            "session": session.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete chat session"""
    chatbot = get_chatbot_core()
    try:
        success = chatbot.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "message": "Session deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Message Endpoints

@router.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, request: SendMessageRequest):
    """Send a message to chat session"""
    chatbot = get_chatbot_core()
    try:
        result = await chatbot.process_message(
            session_id=session_id,
            user_message=request.message,
            metadata=request.metadata
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Message processing failed"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str, limit: Optional[int] = None, message_type: Optional[str] = None):
    """Get messages from chat session"""
    chatbot = get_chatbot_core()
    try:
        session = chatbot.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Convert message_type string to enum if provided
        type_filter = None
        if message_type:
            from ..chatbot.chat_session import MessageType
            try:
                type_filter = MessageType(message_type.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid message type: {message_type}")
        
        messages = session.get_messages(limit=limit, message_type=type_filter)
        
        return {
            "success": True,
            "messages": [msg.to_dict() for msg in messages],
            "count": len(messages),
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/history")
async def get_conversation_history(session_id: str, limit: int = 20):
    """Get conversation history in OpenAI format"""
    chatbot = get_chatbot_core()
    try:
        session = chatbot.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        history = session.get_conversation_history(limit=limit)
        
        return {
            "success": True,
            "history": history,
            "count": len(history),
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Command Endpoints

@router.get("/commands")
async def list_commands(include_admin: bool = False):
    """List available chat commands"""
    chatbot = get_chatbot_core()
    try:
        commands = chatbot.command_processor.get_command_list(include_admin=include_admin)
        
        return {
            "success": True,
            "commands": [
                {
                    "name": cmd.name,
                    "type": cmd.type.value,
                    "description": cmd.description,
                    "usage": cmd.usage,
                    "aliases": cmd.aliases,
                    "admin_only": cmd.admin_only
                } for cmd in commands
            ],
            "count": len(commands)
        }
    except Exception as e:
        logger.error(f"Error listing commands: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/commands")
async def execute_command(session_id: str, command: str):
    """Execute a chat command"""
    chatbot = get_chatbot_core()
    try:
        # Process as a regular message (will be detected as command)
        result = await chatbot.process_message(
            session_id=session_id,
            user_message=command
        )
        
        return result
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Provider Integration Endpoints

@router.get("/providers")
async def get_available_providers():
    """Get available AI providers"""
    chatbot = get_chatbot_core()
    try:
        providers = await chatbot.ai_integration.get_available_providers()
        health = await chatbot.ai_integration.get_provider_health()
        
        return {
            "success": True,
            "providers": [
                {
                    "name": provider,
                    "healthy": health.get(provider, False)
                } for provider in providers
            ]
        }
    except Exception as e:
        logger.error(f"Error getting providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers/{provider}/models")
async def get_provider_models(provider: str):
    """Get available models for a provider"""
    chatbot = get_chatbot_core()
    try:
        models = await chatbot.ai_integration.get_available_models(provider)
        
        return {
            "success": True,
            "provider": provider,
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        logger.error(f"Error getting models for provider {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Management Endpoints

@router.post("/cleanup")
async def cleanup_old_sessions(max_age_hours: int = 24):
    """Clean up old chat sessions"""
    chatbot = get_chatbot_core()
    try:
        count = await chatbot.cleanup_old_sessions(max_age_hours)
        return {
            "success": True,
            "message": f"Cleaned up {count} old sessions",
            "count": count
        }
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    chatbot = get_chatbot_core()
    try:
        status = await chatbot.get_system_status()
        return {
            "status": "healthy",
            "timestamp": status["timestamp"],
            "chatbot_status": status.get("chatbot", {}).get("status", "unknown")
        }
    except Exception as e:
        logger.error(f"Chatbot health check failed: {e}")
        raise HTTPException(status_code=500, detail="Chatbot system unhealthy")

# Export router for main app
__all__ = ["router"]