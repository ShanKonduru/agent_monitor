"""
MCP Protocol Data Models
Defines message formats and communication protocol for Model Context Protocol
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
import uuid

class MessageType(Enum):
    """MCP Message Types"""
    CONTEXT_SHARE = "context_share"
    CONVERSATION_START = "conversation_start"
    CONVERSATION_MESSAGE = "conversation_message" 
    CONVERSATION_END = "conversation_end"
    MEMORY_STORE = "memory_store"
    MEMORY_RETRIEVE = "memory_retrieve"
    AGENT_REGISTER = "agent_register"
    AGENT_STATUS = "agent_status"
    SYSTEM_BROADCAST = "system_broadcast"

class AgentType(Enum):
    """Agent Types in MCP Network"""
    AI_PROVIDER = "ai_provider"
    CHATBOT = "chatbot"
    MONITOR_AGENT = "monitor_agent"
    DASHBOARD = "dashboard"
    EXTERNAL_CLIENT = "external_client"

@dataclass
class MCPMessage:
    """Base MCP Message"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.CONTEXT_SHARE
    sender_id: str = ""
    sender_type: AgentType = AgentType.EXTERNAL_CLIENT
    recipient_id: Optional[str] = None  # None for broadcast
    timestamp: datetime = field(default_factory=datetime.now)
    payload: Dict[str, Any] = field(default_factory=dict)
    conversation_id: Optional[str] = None
    thread_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'type': self.type.value,
            'sender_id': self.sender_id,
            'sender_type': self.sender_type.value,
            'recipient_id': self.recipient_id,
            'timestamp': self.timestamp.isoformat(),
            'payload': self.payload,
            'conversation_id': self.conversation_id,
            'thread_id': self.thread_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """Create from dictionary"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            type=MessageType(data.get('type', MessageType.CONTEXT_SHARE.value)),
            sender_id=data.get('sender_id', ''),
            sender_type=AgentType(data.get('sender_type', AgentType.EXTERNAL_CLIENT.value)),
            recipient_id=data.get('recipient_id'),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            payload=data.get('payload', {}),
            conversation_id=data.get('conversation_id'),
            thread_id=data.get('thread_id')
        )

@dataclass
class MCPRequest(MCPMessage):
    """MCP Request Message"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    expects_response: bool = True
    timeout_seconds: int = 30

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'request_id': self.request_id,
            'expects_response': self.expects_response,
            'timeout_seconds': self.timeout_seconds
        })
        return data

@dataclass
class MCPResponse(MCPMessage):
    """MCP Response Message"""
    request_id: str = ""
    success: bool = True
    error_message: Optional[str] = None
    response_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'request_id': self.request_id,
            'success': self.success,
            'error_message': self.error_message,
            'response_data': self.response_data
        })
        return data

@dataclass
class ContextData:
    """Context data shared between agents"""
    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context_type: str = "general"  # general, conversation, system, agent_state
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def is_expired(self) -> bool:
        """Check if context data has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

@dataclass
class AgentInfo:
    """Information about registered agents"""
    agent_id: str
    agent_type: AgentType
    name: str
    capabilities: List[str] = field(default_factory=list)
    status: str = "active"  # active, inactive, busy, error
    last_seen: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type.value,
            'name': self.name,
            'capabilities': self.capabilities,
            'status': self.status,
            'last_seen': self.last_seen.isoformat(),
            'metadata': self.metadata
        }