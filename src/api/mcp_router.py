"""
FastAPI Router for MCP (Model Context Protocol) Server
Provides REST API endpoints for MCP functionality
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

from ..mcp.mcp_server import MCPServer
from ..mcp.protocol import MCPMessage, MCPRequest, MessageType, AgentType

logger = logging.getLogger(__name__)

# Pydantic models for API requests
class ContextShareRequest(BaseModel):
    context_type: str = "general"
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    expires_in_minutes: Optional[int] = None
    recipient_id: Optional[str] = None

class ConversationStartRequest(BaseModel):
    title: str
    participants: List[str]
    metadata: Optional[Dict[str, Any]] = None

class ConversationMessageRequest(BaseModel):
    conversation_id: str
    content: str
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None

class AgentRegisterRequest(BaseModel):
    agent_id: str
    agent_type: str
    name: str
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentStatusRequest(BaseModel):
    agent_id: str
    status: str
    metadata: Optional[Dict[str, Any]] = None

class MemoryStoreRequest(BaseModel):
    memory_type: str = "general"
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class MemoryRetrieveRequest(BaseModel):
    context_id: Optional[str] = None
    memory_type: Optional[str] = None

# Global MCP server instance
mcp_server: Optional[MCPServer] = None

def get_mcp_server() -> MCPServer:
    """Get the MCP server instance"""
    global mcp_server
    if mcp_server is None:
        mcp_server = MCPServer()
        # Note: In production, you'd want to start this properly with async context
        # For now, we'll initialize synchronously
        logger.info("MCP Server initialized for API")
    return mcp_server

# Create router
router = APIRouter(prefix="/api/v1/mcp", tags=["MCP"])

@router.get("/status")
async def get_mcp_status():
    """Get MCP server status"""
    server = get_mcp_server()
    return {
        "status": "running",
        "message": "MCP Server is operational",
        "statistics": server.get_statistics()
    }

@router.get("/statistics")
async def get_statistics():
    """Get detailed MCP server statistics"""
    server = get_mcp_server()
    return server.get_statistics()

# Context Management Endpoints

@router.post("/context/share")
async def share_context(request: ContextShareRequest):
    """Share context data"""
    server = get_mcp_server()
    
    # Create MCP message
    message = MCPRequest(
        type=MessageType.CONTEXT_SHARE,
        sender_id="api_client",
        sender_type=AgentType.EXTERNAL_CLIENT,
        recipient_id=request.recipient_id,
        payload={
            "context_type": request.context_type,
            "data": request.data,
            "metadata": request.metadata or {},
            "expires_in_minutes": request.expires_in_minutes
        }
    )
    
    try:
        response = await server.process_message(message.to_dict())
        if response and response.success:
            return {
                "success": True,
                "context_id": response.response_data.get("context_id"),
                "message": response.response_data.get("message")
            }
        else:
            error_msg = response.error_message if response else "Unknown error"
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error sharing context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context")
async def get_contexts(context_type: Optional[str] = None):
    """Get contexts, optionally filtered by type"""
    server = get_mcp_server()
    try:
        contexts = server.get_contexts(context_type)
        return {
            "success": True,
            "contexts": contexts,
            "count": len(contexts)
        }
    except Exception as e:
        logger.error(f"Error getting contexts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/store")
async def store_memory(request: MemoryStoreRequest):
    """Store memory data"""
    server = get_mcp_server()
    
    message = MCPRequest(
        type=MessageType.MEMORY_STORE,
        sender_id="api_client",
        sender_type=AgentType.EXTERNAL_CLIENT,
        payload={
            "memory_type": request.memory_type,
            "data": request.data,
            "metadata": request.metadata or {}
        }
    )
    
    try:
        response = await server.process_message(message.to_dict())
        if response and response.success:
            return {
                "success": True,
                "context_id": response.response_data.get("context_id"),
                "message": response.response_data.get("message")
            }
        else:
            error_msg = response.error_message if response else "Unknown error"
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/retrieve")
async def retrieve_memory(request: MemoryRetrieveRequest):
    """Retrieve memory data"""
    server = get_mcp_server()
    
    message = MCPRequest(
        type=MessageType.MEMORY_RETRIEVE,
        sender_id="api_client",
        sender_type=AgentType.EXTERNAL_CLIENT,
        payload={
            "context_id": request.context_id,
            "memory_type": request.memory_type
        }
    )
    
    try:
        response = await server.process_message(message.to_dict())
        if response and response.success:
            return {
                "success": True,
                "data": response.response_data
            }
        else:
            error_msg = response.error_message if response else "Unknown error"
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error retrieving memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Conversation Management Endpoints

@router.post("/conversation/start")
async def start_conversation(request: ConversationStartRequest):
    """Start a new conversation"""
    server = get_mcp_server()
    
    message = MCPRequest(
        type=MessageType.CONVERSATION_START,
        sender_id="api_client",
        sender_type=AgentType.EXTERNAL_CLIENT,
        payload={
            "title": request.title,
            "participants": request.participants,
            "metadata": request.metadata or {}
        }
    )
    
    try:
        response = await server.process_message(message.to_dict())
        if response and response.success:
            return {
                "success": True,
                "conversation_id": response.response_data.get("conversation_id"),
                "message": response.response_data.get("message")
            }
        else:
            error_msg = response.error_message if response else "Unknown error"
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation/message")
async def send_conversation_message(request: ConversationMessageRequest):
    """Send a message to a conversation"""
    server = get_mcp_server()
    
    message = MCPMessage(
        type=MessageType.CONVERSATION_MESSAGE,
        sender_id="api_client",
        sender_type=AgentType.EXTERNAL_CLIENT,
        conversation_id=request.conversation_id,
        payload={
            "content": request.content,
            "message_type": request.message_type,
            "metadata": request.metadata or {}
        }
    )
    
    try:
        response = await server.process_message(message.to_dict())
        if response and response.success:
            return {
                "success": True,
                "message": response.response_data.get("message")
            }
        else:
            error_msg = response.error_message if response else "Unknown error"
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error sending conversation message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations")
async def get_conversations(participant_id: Optional[str] = None):
    """Get conversations, optionally filtered by participant"""
    server = get_mcp_server()
    try:
        conversations = server.get_conversations(participant_id)
        return {
            "success": True,
            "conversations": conversations,
            "count": len(conversations)
        }
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get specific conversation details"""
    server = get_mcp_server()
    try:
        conversation = server.get_conversation(conversation_id)
        if conversation:
            return {
                "success": True,
                "conversation": conversation
            }
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, limit: int = 100):
    """Get messages for a conversation"""
    server = get_mcp_server()
    try:
        messages = server.get_conversation_messages(conversation_id, limit)
        return {
            "success": True,
            "messages": messages,
            "count": len(messages),
            "conversation_id": conversation_id
        }
    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation/{conversation_id}/end")
async def end_conversation(conversation_id: str):
    """End a conversation"""
    server = get_mcp_server()
    
    message = MCPRequest(
        type=MessageType.CONVERSATION_END,
        sender_id="api_client",
        sender_type=AgentType.EXTERNAL_CLIENT,
        conversation_id=conversation_id,
        payload={"conversation_id": conversation_id}
    )
    
    try:
        response = await server.process_message(message.to_dict())
        if response and response.success:
            return {
                "success": True,
                "message": response.response_data.get("message")
            }
        else:
            error_msg = response.error_message if response else "Unknown error"
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent Management Endpoints

@router.post("/agent/register")
async def register_agent(request: AgentRegisterRequest):
    """Register a new agent"""
    server = get_mcp_server()
    
    message = MCPRequest(
        type=MessageType.AGENT_REGISTER,
        sender_id=request.agent_id,
        sender_type=AgentType.EXTERNAL_CLIENT,
        payload={
            "agent_type": request.agent_type,
            "name": request.name,
            "capabilities": request.capabilities or [],
            "metadata": request.metadata or {}
        }
    )
    
    try:
        response = await server.process_message(message.to_dict())
        if response and response.success:
            return {
                "success": True,
                "message": response.response_data.get("message")
            }
        else:
            error_msg = response.error_message if response else "Unknown error"
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error registering agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/status")
async def update_agent_status(request: AgentStatusRequest):
    """Update agent status"""
    server = get_mcp_server()
    
    message = MCPRequest(
        type=MessageType.AGENT_STATUS,
        sender_id=request.agent_id,
        sender_type=AgentType.EXTERNAL_CLIENT,
        payload={
            "status": request.status,
            "metadata": request.metadata or {}
        }
    )
    
    try:
        response = await server.process_message(message.to_dict())
        if response and response.success:
            return {
                "success": True,
                "message": response.response_data.get("message")
            }
        else:
            error_msg = response.error_message if response else "Unknown error"
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Error updating agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def get_agents(agent_type: Optional[str] = None):
    """Get registered agents, optionally filtered by type"""
    server = get_mcp_server()
    try:
        agents = server.get_agents(agent_type)
        return {
            "success": True,
            "agents": agents,
            "count": len(agents)
        }
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility Endpoints

@router.post("/cleanup")
async def cleanup_expired():
    """Clean up expired contexts and data"""
    server = get_mcp_server()
    try:
        # This would need to be implemented in the server
        count = server.context_manager.cleanup_expired_contexts()
        return {
            "success": True,
            "message": f"Cleaned up {count} expired contexts"
        }
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    server = get_mcp_server()
    try:
        stats = server.get_statistics()
        return {
            "status": "healthy",
            "timestamp": stats["server_info"]["uptime"],
            "version": stats["server_info"]["version"]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="MCP Server unhealthy")

# Export router for main app
__all__ = ["router"]