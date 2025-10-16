"""
Database package for the Agent Monitor Framework.
Provides persistent storage and time-series data management.
"""

from .connection import db_manager, get_db_session, init_database, cleanup_database
from .models import (
    Agent, AgentConfiguration, AgentTag, AgentGroup, AgentGroupMembership,
    User, UserSession, APIKey,
    AlertRule, AlertInstance, NotificationChannel, AlertNotification,
    AuditLog,
    AgentStatus, AgentType, DeploymentType, UserRole, AlertSeverity, AlertStatus
)
from .influx_client import influx_client, TimeSeriesQuery

__all__ = [
    # Connection management
    "db_manager", "get_db_session", "init_database", "cleanup_database",
    
    # Models
    "Agent", "AgentConfiguration", "AgentTag", "AgentGroup", "AgentGroupMembership",
    "User", "UserSession", "APIKey",
    "AlertRule", "AlertInstance", "NotificationChannel", "AlertNotification",
    "AuditLog",
    
    # Enums
    "AgentStatus", "AgentType", "DeploymentType", "UserRole", "AlertSeverity", "AlertStatus",
    
    # Time-series
    "influx_client", "TimeSeriesQuery"
]