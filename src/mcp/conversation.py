"""
Conversation Management for MCP
Handles conversation threading and context management
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import logging

from .protocol import MCPMessage, AgentType

logger = logging.getLogger(__name__)

@dataclass
class ConversationThread:
    """Individual thread within a conversation"""
    thread_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    title: str = "New Thread"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, completed, archived
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.now()

@dataclass 
class Conversation:
    """Multi-agent conversation container"""
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Conversation"
    participants: List[str] = field(default_factory=list)  # agent IDs
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, paused, completed, archived
    metadata: Dict[str, Any] = field(default_factory=dict)
    threads: Dict[str, ConversationThread] = field(default_factory=dict)
    
    def add_participant(self, agent_id: str) -> bool:
        """Add participant to conversation"""
        if agent_id not in self.participants:
            self.participants.append(agent_id)
            self.update_timestamp()
            logger.info(f"Added participant {agent_id} to conversation {self.conversation_id}")
            return True
        return False
    
    def remove_participant(self, agent_id: str) -> bool:
        """Remove participant from conversation"""
        if agent_id in self.participants:
            self.participants.remove(agent_id)
            self.update_timestamp()
            logger.info(f"Removed participant {agent_id} from conversation {self.conversation_id}")
            return True
        return False
    
    def create_thread(self, title: str = "New Thread", metadata: Optional[Dict[str, Any]] = None) -> ConversationThread:
        """Create new thread in conversation"""
        thread = ConversationThread(
            conversation_id=self.conversation_id,
            title=title,
            metadata=metadata or {}
        )
        self.threads[thread.thread_id] = thread
        self.update_timestamp()
        logger.info(f"Created thread {thread.thread_id} in conversation {self.conversation_id}")
        return thread
    
    def get_thread(self, thread_id: str) -> Optional[ConversationThread]:
        """Get thread by ID"""
        return self.threads.get(thread_id)
    
    def list_threads(self, status: Optional[str] = None) -> List[ConversationThread]:
        """List threads, optionally filtered by status"""
        threads = list(self.threads.values())
        if status:
            threads = [t for t in threads if t.status == status]
        return sorted(threads, key=lambda t: t.updated_at, reverse=True)
    
    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.now()
    
    def get_active_participants(self) -> List[str]:
        """Get list of active participants"""
        # For now, return all participants
        # Could be enhanced to check agent status from memory store
        return self.participants.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'conversation_id': self.conversation_id,
            'title': self.title,
            'participants': self.participants,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status,
            'metadata': self.metadata,
            'threads': {tid: {
                'thread_id': thread.thread_id,
                'title': thread.title,
                'created_at': thread.created_at.isoformat(),
                'updated_at': thread.updated_at.isoformat(),
                'status': thread.status,
                'metadata': thread.metadata
            } for tid, thread in self.threads.items()}
        }

class ConversationManager:
    """Manages conversations and threading"""
    
    def __init__(self, memory_store=None):
        """Initialize conversation manager"""
        self.memory_store = memory_store
        self.active_conversations: Dict[str, Conversation] = {}
        logger.info("ConversationManager initialized")
    
    def create_conversation(self, title: str, participants: List[str], 
                          metadata: Optional[Dict[str, Any]] = None) -> Conversation:
        """Create new conversation"""
        conversation = Conversation(
            title=title,
            participants=participants.copy(),
            metadata=metadata or {}
        )
        
        self.active_conversations[conversation.conversation_id] = conversation
        
        # Store in memory if available
        if self.memory_store:
            self.memory_store.store_conversation(conversation)
        
        logger.info(f"Created conversation {conversation.conversation_id} with {len(participants)} participants")
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        # Check active conversations first
        if conversation_id in self.active_conversations:
            return self.active_conversations[conversation_id]
        
        # Try to load from memory store
        if self.memory_store:
            stored_conversation = self.memory_store.get_conversation(conversation_id)
            if stored_conversation:
                self.active_conversations[conversation_id] = stored_conversation
                return stored_conversation
        
        return None
    
    def add_message_to_conversation(self, message: MCPMessage, create_if_missing: bool = True) -> bool:
        """Add message to conversation, creating conversation if needed"""
        if not message.conversation_id:
            logger.warning("Message has no conversation_id")
            return False
        
        conversation = self.get_conversation(message.conversation_id)
        
        if not conversation and create_if_missing:
            # Create new conversation
            conversation = self.create_conversation(
                title=f"Conversation with {message.sender_id}",
                participants=[message.sender_id],
                metadata={"auto_created": True}
            )
            logger.info(f"Auto-created conversation {conversation.conversation_id} for message")
        
        if not conversation:
            logger.error(f"Could not find or create conversation {message.conversation_id}")
            return False
        
        # Add sender as participant if not already
        conversation.add_participant(message.sender_id)
        
        # Add recipient as participant if specified
        if message.recipient_id:
            conversation.add_participant(message.recipient_id)
        
        # Update conversation timestamp
        conversation.update_timestamp()
        
        # Store message in memory if available
        if self.memory_store:
            self.memory_store.store_message(message)
            self.memory_store.store_conversation(conversation)
        
        return True
    
    def list_conversations(self, participant_id: Optional[str] = None) -> List[Conversation]:
        """List conversations, optionally filtered by participant"""
        conversations = list(self.active_conversations.values())
        
        # Load additional conversations from memory store
        if self.memory_store:
            stored_conversations = self.memory_store.list_conversations(participant_id)
            for conv_data in stored_conversations:
                conv_id = conv_data['conversation_id']
                if conv_id not in self.active_conversations:
                    # Convert back to Conversation object
                    conversation = Conversation(
                        conversation_id=conv_id,
                        title=conv_data['title'],
                        participants=conv_data['participants'],
                        created_at=datetime.fromisoformat(conv_data['created_at']),
                        updated_at=datetime.fromisoformat(conv_data['updated_at']),
                        status=conv_data['status'],
                        metadata=conv_data['metadata']
                    )
                    conversations.append(conversation)
        
        # Filter by participant if specified
        if participant_id:
            conversations = [c for c in conversations if participant_id in c.participants]
        
        return sorted(conversations, key=lambda c: c.updated_at, reverse=True)
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages for a conversation"""
        if self.memory_store:
            return self.memory_store.get_conversation_messages(conversation_id, limit)
        return []
    
    def archive_conversation(self, conversation_id: str) -> bool:
        """Archive a conversation"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.status = "archived"
            conversation.update_timestamp()
            
            if self.memory_store:
                self.memory_store.store_conversation(conversation)
            
            # Remove from active conversations
            if conversation_id in self.active_conversations:
                del self.active_conversations[conversation_id]
            
            logger.info(f"Archived conversation {conversation_id}")
            return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        stats = {
            'active_conversations': len(self.active_conversations),
            'total_participants': 0,
            'total_threads': 0
        }
        
        for conversation in self.active_conversations.values():
            stats['total_participants'] += len(conversation.participants)
            stats['total_threads'] += len(conversation.threads)
        
        # Add memory store statistics if available
        if self.memory_store:
            memory_stats = self.memory_store.get_statistics()
            stats.update({
                'stored_conversations': memory_stats.get('total_conversations', 0),
                'stored_messages': memory_stats.get('total_messages', 0)
            })
        
        return stats