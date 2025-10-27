"""
MCP Memory Store
Persistent storage for conversations, context, and agent memories
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import asdict
import logging

from .protocol import ContextData, MCPMessage, AgentInfo
from .conversation import Conversation, ConversationThread

logger = logging.getLogger(__name__)

class MemoryStore:
    """Persistent memory storage for MCP server"""
    
    def __init__(self, db_path: str = "data/mcp_memory.db"):
        """Initialize memory store with SQLite database"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Context storage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contexts (
                    context_id TEXT PRIMARY KEY,
                    context_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    metadata TEXT,
                    expires_at TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    sender_id TEXT NOT NULL,
                    sender_type TEXT NOT NULL,
                    recipient_id TEXT,
                    timestamp TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    conversation_id TEXT,
                    thread_id TEXT
                )
            """)
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    title TEXT,
                    participants TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    metadata TEXT
                )
            """)
            
            # Conversation threads table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_threads (
                    thread_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    title TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
                )
            """)
            
            # Agents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    agent_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    capabilities TEXT,
                    status TEXT DEFAULT 'active',
                    last_seen TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contexts_type ON contexts(context_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contexts_expires ON contexts(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
            
            conn.commit()
    
    def store_context(self, context: ContextData) -> bool:
        """Store context data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO contexts 
                    (context_id, context_type, data, metadata, expires_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    context.context_id,
                    context.context_type,
                    json.dumps(context.data),
                    json.dumps(context.metadata),
                    context.expires_at.isoformat() if context.expires_at else None,
                    context.created_at.isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error storing context: {e}")
            return False
    
    def retrieve_context(self, context_id: str) -> Optional[ContextData]:
        """Retrieve context by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT context_id, context_type, data, metadata, expires_at, created_at
                    FROM contexts WHERE context_id = ?
                """, (context_id,))
                
                row = cursor.fetchone()
                if row:
                    context = ContextData(
                        context_id=row[0],
                        context_type=row[1],
                        data=json.loads(row[2]),
                        metadata=json.loads(row[3]) if row[3] else {},
                        expires_at=datetime.fromisoformat(row[4]) if row[4] else None,
                        created_at=datetime.fromisoformat(row[5])
                    )
                    
                    # Check if expired
                    if context.is_expired():
                        self.delete_context(context_id)
                        return None
                    
                    return context
                return None
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return None
    
    def retrieve_contexts_by_type(self, context_type: str) -> List[ContextData]:
        """Retrieve all contexts of a specific type"""
        contexts = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT context_id, context_type, data, metadata, expires_at, created_at
                    FROM contexts WHERE context_type = ?
                    ORDER BY created_at DESC
                """, (context_type,))
                
                for row in cursor.fetchall():
                    context = ContextData(
                        context_id=row[0],
                        context_type=row[1],
                        data=json.loads(row[2]),
                        metadata=json.loads(row[3]) if row[3] else {},
                        expires_at=datetime.fromisoformat(row[4]) if row[4] else None,
                        created_at=datetime.fromisoformat(row[5])
                    )
                    
                    if not context.is_expired():
                        contexts.append(context)
                    else:
                        self.delete_context(context.context_id)
        except Exception as e:
            logger.error(f"Error retrieving contexts by type: {e}")
        
        return contexts
    
    def delete_context(self, context_id: str) -> bool:
        """Delete context by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM contexts WHERE context_id = ?", (context_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting context: {e}")
            return False
    
    def store_message(self, message: MCPMessage) -> bool:
        """Store message"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages 
                    (message_id, type, sender_id, sender_type, recipient_id, timestamp, 
                     payload, conversation_id, thread_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.id,
                    message.type.value,
                    message.sender_id,
                    message.sender_type.value,
                    message.recipient_id,
                    message.timestamp.isoformat(),
                    json.dumps(message.payload),
                    message.conversation_id,
                    message.thread_id
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error storing message: {e}")
            return False
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages for a conversation"""
        messages = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT message_id, type, sender_id, sender_type, recipient_id, 
                           timestamp, payload, conversation_id, thread_id
                    FROM messages 
                    WHERE conversation_id = ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                """, (conversation_id, limit))
                
                for row in cursor.fetchall():
                    messages.append({
                        'message_id': row[0],
                        'type': row[1],
                        'sender_id': row[2],
                        'sender_type': row[3],
                        'recipient_id': row[4],
                        'timestamp': row[5],
                        'payload': json.loads(row[6]),
                        'conversation_id': row[7],
                        'thread_id': row[8]
                    })
        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
        
        return messages
    
    def store_conversation(self, conversation: Conversation) -> bool:
        """Store conversation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO conversations 
                    (conversation_id, title, participants, created_at, updated_at, status, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    conversation.conversation_id,
                    conversation.title,
                    json.dumps(conversation.participants),
                    conversation.created_at.isoformat(),
                    conversation.updated_at.isoformat(),
                    conversation.status,
                    json.dumps(conversation.metadata)
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
            return False
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT conversation_id, title, participants, created_at, updated_at, status, metadata
                    FROM conversations WHERE conversation_id = ?
                """, (conversation_id,))
                
                row = cursor.fetchone()
                if row:
                    return Conversation(
                        conversation_id=row[0],
                        title=row[1],
                        participants=json.loads(row[2]),
                        created_at=datetime.fromisoformat(row[3]),
                        updated_at=datetime.fromisoformat(row[4]),
                        status=row[5],
                        metadata=json.loads(row[6])
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None
    
    def list_conversations(self, participant_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List conversations, optionally filtered by participant"""
        conversations = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if participant_id:
                    cursor.execute("""
                        SELECT conversation_id, title, participants, created_at, updated_at, status, metadata
                        FROM conversations 
                        WHERE participants LIKE ?
                        ORDER BY updated_at DESC
                        LIMIT ?
                    """, (f'%"{participant_id}"%', limit))
                else:
                    cursor.execute("""
                        SELECT conversation_id, title, participants, created_at, updated_at, status, metadata
                        FROM conversations 
                        ORDER BY updated_at DESC
                        LIMIT ?
                    """, (limit,))
                
                for row in cursor.fetchall():
                    conversations.append({
                        'conversation_id': row[0],
                        'title': row[1],
                        'participants': json.loads(row[2]),
                        'created_at': row[3],
                        'updated_at': row[4],
                        'status': row[5],
                        'metadata': json.loads(row[6])
                    })
        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
        
        return conversations
    
    def store_agent(self, agent: AgentInfo) -> bool:
        """Store agent information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO agents 
                    (agent_id, agent_type, name, capabilities, status, last_seen, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    agent.agent_id,
                    agent.agent_type.value,
                    agent.name,
                    json.dumps(agent.capabilities),
                    agent.status,
                    agent.last_seen.isoformat(),
                    json.dumps(agent.metadata)
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error storing agent: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT agent_id, agent_type, name, capabilities, status, last_seen, metadata
                    FROM agents WHERE agent_id = ?
                """, (agent_id,))
                
                row = cursor.fetchone()
                if row:
                    from .protocol import AgentType
                    return AgentInfo(
                        agent_id=row[0],
                        agent_type=AgentType(row[1]),
                        name=row[2],
                        capabilities=json.loads(row[3]),
                        status=row[4],
                        last_seen=datetime.fromisoformat(row[5]),
                        metadata=json.loads(row[6])
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting agent: {e}")
            return None
    
    def list_agents(self, agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List agents, optionally filtered by type"""
        agents = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if agent_type:
                    cursor.execute("""
                        SELECT agent_id, agent_type, name, capabilities, status, last_seen, metadata
                        FROM agents WHERE agent_type = ?
                        ORDER BY last_seen DESC
                    """, (agent_type,))
                else:
                    cursor.execute("""
                        SELECT agent_id, agent_type, name, capabilities, status, last_seen, metadata
                        FROM agents 
                        ORDER BY last_seen DESC
                    """)
                
                for row in cursor.fetchall():
                    agents.append({
                        'agent_id': row[0],
                        'agent_type': row[1],
                        'name': row[2],
                        'capabilities': json.loads(row[3]),
                        'status': row[4],
                        'last_seen': row[5],
                        'metadata': json.loads(row[6])
                    })
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
        
        return agents
    
    def cleanup_expired_contexts(self) -> int:
        """Remove expired contexts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                cursor.execute("""
                    DELETE FROM contexts 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (now,))
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error cleaning expired contexts: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory store statistics"""
        stats = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count contexts
                cursor.execute("SELECT COUNT(*) FROM contexts")
                stats['total_contexts'] = cursor.fetchone()[0]
                
                # Count messages
                cursor.execute("SELECT COUNT(*) FROM messages")
                stats['total_messages'] = cursor.fetchone()[0]
                
                # Count conversations
                cursor.execute("SELECT COUNT(*) FROM conversations")
                stats['total_conversations'] = cursor.fetchone()[0]
                
                # Count agents
                cursor.execute("SELECT COUNT(*) FROM agents")
                stats['total_agents'] = cursor.fetchone()[0]
                
                # Active conversations
                cursor.execute("SELECT COUNT(*) FROM conversations WHERE status = 'active'")
                stats['active_conversations'] = cursor.fetchone()[0]
                
                # Active agents
                cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'active'")
                stats['active_agents'] = cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
        
        return stats