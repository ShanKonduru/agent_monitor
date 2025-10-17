"""
Database models for the Agent Monitor Framework using SQLAlchemy.
Provides persistent storage for agent metadata, users, alerts, and configurations.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, 
    ForeignKey, JSON, Index, UniqueConstraint, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

Base = declarative_base()


class AgentStatus(PyEnum):
    """Agent status enumeration"""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    MAINTENANCE = "MAINTENANCE"
    UNKNOWN = "UNKNOWN"


class AgentType(PyEnum):
    """Agent type enumeration"""
    LLM_AGENT = "LLM_AGENT"
    TASK_AGENT = "TASK_AGENT"
    API_AGENT = "API_AGENT"
    MONITOR_AGENT = "MONITOR_AGENT"
    DATA_AGENT = "DATA_AGENT"
    CUSTOM = "CUSTOM"


class DeploymentType(PyEnum):
    """Deployment type enumeration"""
    LOCAL = "LOCAL"
    DOCKER = "DOCKER"
    KUBERNETES = "KUBERNETES"
    CLOUD = "CLOUD"
    EDGE = "EDGE"


class UserRole(PyEnum):
    """User role enumeration"""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class AlertSeverity(PyEnum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(PyEnum):
    """Alert status enumeration"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"


# Core Agent Models
class Agent(Base):
    """Main agent registry table"""
    __tablename__ = "agents"
    
    id = Column(String(36), primary_key=True)  # UUID
    name = Column(String(255), nullable=False)
    type = Column(Enum(AgentType), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    deployment_type = Column(Enum(DeploymentType), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer)
    environment = Column(String(100), nullable=False, default="production")
    status = Column(Enum(AgentStatus), nullable=False, default=AgentStatus.OFFLINE)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_heartbeat = Column(DateTime(timezone=True))
    last_metrics_received = Column(DateTime(timezone=True))
    
    # Metadata
    agent_metadata = Column(JSON, default={})
    
    # Relationships
    configurations = relationship("AgentConfiguration", back_populates="agent", cascade="all, delete-orphan")
    tags = relationship("AgentTag", back_populates="agent", cascade="all, delete-orphan")
    groups = relationship("AgentGroupMembership", back_populates="agent")
    alert_instances = relationship("AlertInstance", back_populates="agent")
    
    # Indexes
    __table_args__ = (
        Index('idx_agent_status', 'status'),
        Index('idx_agent_type', 'type'),
        Index('idx_agent_environment', 'environment'),
        Index('idx_agent_host', 'host'),
        Index('idx_agent_last_heartbeat', 'last_heartbeat'),
    )


class AgentConfiguration(Base):
    """Agent configuration key-value store"""
    __tablename__ = "agent_configurations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    config_key = Column(String(255), nullable=False)
    config_value = Column(Text)
    config_type = Column(String(50), default="string")  # string, integer, float, boolean, json
    is_secret = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="configurations")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('agent_id', 'config_key', name='uq_agent_config'),
        Index('idx_agent_config_key', 'config_key'),
    )


class AgentTag(Base):
    """Agent tags for categorization and filtering"""
    __tablename__ = "agent_tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    tag_value = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="tags")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('agent_id', 'tag_name', name='uq_agent_tag'),
        Index('idx_agent_tag_name', 'tag_name'),
        Index('idx_agent_tag_value', 'tag_value'),
    )


# Agent Groups
class AgentGroup(Base):
    """Agent groups for organization and bulk operations"""
    __tablename__ = "agent_groups"
    
    id = Column(String(36), primary_key=True)  # UUID
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    
    # Group configuration
    config = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"))
    
    # Relationships
    memberships = relationship("AgentGroupMembership", back_populates="group", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_group_name', 'name'),
        Index('idx_group_created_by', 'created_by'),
    )


class AgentGroupMembership(Base):
    """Many-to-many relationship between agents and groups"""
    __tablename__ = "agent_group_memberships"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(String(36), ForeignKey("agent_groups.id", ondelete="CASCADE"), nullable=False)
    
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    added_by = Column(String(36), ForeignKey("users.id"))
    
    # Relationships
    agent = relationship("Agent", back_populates="groups")
    group = relationship("AgentGroup", back_populates="memberships")
    added_by_user = relationship("User", foreign_keys=[added_by])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('agent_id', 'group_id', name='uq_agent_group'),
        Index('idx_membership_agent', 'agent_id'),
        Index('idx_membership_group', 'group_id'),
    )


# User Management
class User(Base):
    """User accounts for dashboard access"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)  # UUID
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    created_groups = relationship("AgentGroup", foreign_keys="AgentGroup.created_by")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_username', 'username'),
        Index('idx_user_email', 'email'),
        Index('idx_user_role', 'role'),
        Index('idx_user_active', 'is_active'),
    )


class UserSession(Base):
    """User login sessions"""
    __tablename__ = "user_sessions"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used = Column(DateTime(timezone=True))
    
    # Session metadata
    user_agent = Column(Text)
    ip_address = Column(String(45))  # IPv6 compatible
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_session_token', 'token_hash'),
        Index('idx_session_user', 'user_id'),
        Index('idx_session_expires', 'expires_at'),
    )


class APIKey(Base):
    """API keys for programmatic access"""
    __tablename__ = "api_keys"
    
    id = Column(String(36), primary_key=True)  # UUID
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Permissions and configuration
    permissions = Column(JSON, default=[])  # List of allowed operations
    rate_limit = Column(Integer)  # Requests per minute
    
    # Status and expiration
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    # Indexes
    __table_args__ = (
        Index('idx_api_key_hash', 'key_hash'),
        Index('idx_api_key_user', 'user_id'),
        Index('idx_api_key_active', 'is_active'),
    )


# Alert System
class AlertRule(Base):
    """Alert rule definitions"""
    __tablename__ = "alert_rules"
    
    id = Column(String(36), primary_key=True)  # UUID
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Rule definition
    condition = Column(JSON, nullable=False)  # Alert condition logic
    threshold = Column(Float)
    severity = Column(Enum(AlertSeverity), nullable=False, default=AlertSeverity.MEDIUM)
    
    # Rule configuration
    evaluation_interval = Column(Integer, default=60)  # Seconds
    for_duration = Column(Integer, default=300)  # Seconds (5 minutes)
    
    # Status
    is_enabled = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"))
    
    # Relationships
    instances = relationship("AlertInstance", back_populates="rule", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_rule_name', 'name'),
        Index('idx_alert_rule_enabled', 'is_enabled'),
        Index('idx_alert_rule_severity', 'severity'),
    )


class AlertInstance(Base):
    """Alert instances (fired alerts)"""
    __tablename__ = "alert_instances"
    
    id = Column(String(36), primary_key=True)  # UUID
    rule_id = Column(String(36), ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"))
    
    status = Column(Enum(AlertStatus), nullable=False, default=AlertStatus.ACTIVE)
    severity = Column(Enum(AlertSeverity), nullable=False)
    
    # Alert details
    message = Column(Text, nullable=False)
    details = Column(JSON, default={})  # Additional context
    
    # Timestamps
    triggered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True))
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(String(36), ForeignKey("users.id"))
    
    # Relationships
    rule = relationship("AlertRule", back_populates="instances")
    agent = relationship("Agent", back_populates="alert_instances")
    acknowledged_by_user = relationship("User", foreign_keys=[acknowledged_by])
    notifications = relationship("AlertNotification", back_populates="alert", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_instance_rule', 'rule_id'),
        Index('idx_alert_instance_agent', 'agent_id'),
        Index('idx_alert_instance_status', 'status'),
        Index('idx_alert_instance_triggered', 'triggered_at'),
    )


class NotificationChannel(Base):
    """Notification channels for alerts"""
    __tablename__ = "notification_channels"
    
    id = Column(String(36), primary_key=True)  # UUID
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # email, slack, webhook, etc.
    
    # Channel configuration
    config = Column(JSON, nullable=False)  # Channel-specific settings
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    notifications = relationship("AlertNotification", back_populates="channel")
    
    # Indexes
    __table_args__ = (
        Index('idx_notification_channel_type', 'type'),
        Index('idx_notification_channel_active', 'is_active'),
    )


class AlertNotification(Base):
    """Alert notification delivery tracking"""
    __tablename__ = "alert_notifications"
    
    id = Column(String(36), primary_key=True)  # UUID
    alert_id = Column(String(36), ForeignKey("alert_instances.id", ondelete="CASCADE"), nullable=False)
    channel_id = Column(String(36), ForeignKey("notification_channels.id", ondelete="CASCADE"), nullable=False)
    
    status = Column(String(50), nullable=False, default="pending")  # pending, sent, failed, retry
    attempts = Column(Integer, default=0, nullable=False)
    
    sent_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    alert = relationship("AlertInstance", back_populates="notifications")
    channel = relationship("NotificationChannel", back_populates="notifications")
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_notification_alert', 'alert_id'),
        Index('idx_alert_notification_channel', 'channel_id'),
        Index('idx_alert_notification_status', 'status'),
    )


# Audit and Compliance
class AuditLog(Base):
    """Audit log for tracking system changes"""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey("users.id"))
    
    # Action details
    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.
    resource_type = Column(String(100), nullable=False)  # agent, user, alert_rule, etc.
    resource_id = Column(String(36))
    
    # Request details
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Change details
    old_values = Column(JSON)
    new_values = Column(JSON)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_log_user', 'user_id'),
        Index('idx_audit_log_action', 'action'),
        Index('idx_audit_log_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_log_timestamp', 'timestamp'),
    )