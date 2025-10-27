"""
Chat Session Management
Handles individual chat sessions with conversation history and context
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of chat messages"""
    USER = "user"
    ASSISTANT = "assistant" 
    SYSTEM = "system"
    COMMAND = "command"
    ERROR = "error"
    INFO = "info"

class MessageStatus(Enum):
    """Message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ChatMessage:
    """Individual chat message"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    type: MessageType = MessageType.USER
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    status: MessageStatus = MessageStatus.COMPLETED
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # AI-specific fields
    provider: Optional[str] = None
    model: Optional[str] = None
    tokens_used: int = 0
    latency_ms: int = 0
    cost: float = 0.0
    
    # Context fields
    conversation_id: Optional[str] = None
    thread_id: Optional[str] = None
    parent_message_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'type': self.type.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status.value,
            'metadata': self.metadata,
            'provider': self.provider,
            'model': self.model,
            'tokens_used': self.tokens_used,
            'latency_ms': self.latency_ms,
            'cost': self.cost,
            'conversation_id': self.conversation_id,
            'thread_id': self.thread_id,
            'parent_message_id': self.parent_message_id
        }

@dataclass
class ChatSession:
    """Chat session container"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "anonymous"
    title: str = "New Chat"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, paused, completed, archived
    
    # Session configuration
    ai_provider: str = "local"
    ai_model: str = "llama3.1"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # Message history
    messages: List[ChatMessage] = field(default_factory=list)
    
    # Context and metadata
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # MCP integration
    mcp_conversation_id: Optional[str] = None
    mcp_thread_id: Optional[str] = None
    
    def add_message(self, message_type: MessageType, content: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """Add a message to the session"""
        message = ChatMessage(
            session_id=self.session_id,
            type=message_type,
            content=content,
            metadata=metadata or {},
            conversation_id=self.mcp_conversation_id,
            thread_id=self.mcp_thread_id
        )
        
        # Set parent message ID (previous message)
        if self.messages:
            message.parent_message_id = self.messages[-1].id
        
        self.messages.append(message)
        self.update_timestamp()
        
        logger.debug(f"Added {message_type.value} message to session {self.session_id}")
        return message
    
    def get_messages(self, limit: Optional[int] = None, 
                    message_type: Optional[MessageType] = None) -> List[ChatMessage]:
        """Get messages from session"""
        messages = self.messages
        
        if message_type:
            messages = [msg for msg in messages if msg.type == message_type]
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_conversation_history(self, limit: int = 20) -> List[Dict[str, str]]:
        """Get conversation history in OpenAI format"""
        history = []
        recent_messages = self.messages[-limit:] if limit else self.messages
        
        for message in recent_messages:
            if message.type in [MessageType.USER, MessageType.ASSISTANT]:
                role = "user" if message.type == MessageType.USER else "assistant"
                history.append({
                    "role": role,
                    "content": message.content
                })
        
        return history
    
    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.now()
    
    def get_latest_user_message(self) -> Optional[ChatMessage]:
        """Get the most recent user message"""
        for message in reversed(self.messages):
            if message.type == MessageType.USER:
                return message
        return None
    
    def get_latest_assistant_message(self) -> Optional[ChatMessage]:
        """Get the most recent assistant message"""
        for message in reversed(self.messages):
            if message.type == MessageType.ASSISTANT:
                return message
        return None
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate session statistics"""
        total_messages = len(self.messages)
        user_messages = len([m for m in self.messages if m.type == MessageType.USER])
        assistant_messages = len([m for m in self.messages if m.type == MessageType.ASSISTANT])
        
        total_tokens = sum(m.tokens_used for m in self.messages)
        total_cost = sum(m.cost for m in self.messages)
        
        avg_latency = 0
        if assistant_messages > 0:
            latencies = [m.latency_ms for m in self.messages if m.type == MessageType.ASSISTANT and m.latency_ms > 0]
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
        
        return {
            'session_id': self.session_id,
            'total_messages': total_messages,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'avg_latency_ms': avg_latency,
            'duration_minutes': (self.updated_at - self.created_at).total_seconds() / 60,
            'provider': self.ai_provider,
            'model': self.ai_model
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status,
            'ai_provider': self.ai_provider,
            'ai_model': self.ai_model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'message_count': len(self.messages),
            'context': self.context,
            'metadata': self.metadata,
            'mcp_conversation_id': self.mcp_conversation_id,
            'mcp_thread_id': self.mcp_thread_id,
            'statistics': self.calculate_statistics()
        }

class ChatSessionManager:
    """Manages multiple chat sessions"""
    
    def __init__(self):
        """Initialize session manager"""
        self.sessions: Dict[str, ChatSession] = {}
        logger.info("ChatSessionManager initialized")
    
    def create_session(self, user_id: str = "anonymous", title: str = "New Chat",
                      ai_provider: str = "local", ai_model: str = "llama3.1",
                      **kwargs) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            user_id=user_id,
            title=title,
            ai_provider=ai_provider,
            ai_model=ai_model,
            **kwargs
        )
        
        self.sessions[session.session_id] = session
        
        logger.info(f"Created chat session {session.session_id} for user {user_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def list_sessions(self, user_id: Optional[str] = None, 
                     status: Optional[str] = None) -> List[ChatSession]:
        """List sessions with optional filters"""
        sessions = list(self.sessions.values())
        
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        
        if status:
            sessions = [s for s in sessions if s.status == status]
        
        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted chat session {session_id}")
            return True
        return False
    
    def archive_session(self, session_id: str) -> bool:
        """Archive a session"""
        session = self.get_session(session_id)
        if session:
            session.status = "archived"
            session.update_timestamp()
            logger.info(f"Archived chat session {session_id}")
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get session manager statistics"""
        total_sessions = len(self.sessions)
        active_sessions = len([s for s in self.sessions.values() if s.status == "active"])
        
        total_messages = sum(len(s.messages) for s in self.sessions.values())
        
        providers = {}
        models = {}
        
        for session in self.sessions.values():
            provider = session.ai_provider
            model = session.ai_model
            
            providers[provider] = providers.get(provider, 0) + 1
            models[model] = models.get(model, 0) + 1
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'total_messages': total_messages,
            'providers': providers,
            'models': models
        }