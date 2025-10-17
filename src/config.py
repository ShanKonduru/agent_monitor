"""
Configuration management for the Agent Monitor Framework.
"""

import os
from typing import Optional, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConfig(BaseModel):
    """Database configuration"""
    postgres_url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", 
            "sqlite+aiosqlite:///./agent_monitor.db"  # Default to SQLite for development
        )
    )
    influxdb_url: str = Field(
        default_factory=lambda: os.getenv("INFLUXDB_URL", "http://localhost:8086")
    )
    influxdb_token: Optional[str] = Field(
        default_factory=lambda: os.getenv("INFLUXDB_TOKEN")
    )
    influxdb_org: str = Field(
        default_factory=lambda: os.getenv("INFLUXDB_ORG", "monitor")
    )
    influxdb_bucket: str = Field(
        default_factory=lambda: os.getenv("INFLUXDB_BUCKET", "metrics")
    )


class RedisConfig(BaseModel):
    """Redis configuration"""
    redis_url: str = Field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379")
    )
    redis_password: Optional[str] = Field(
        default_factory=lambda: os.getenv("REDIS_PASSWORD")
    )


class SecurityConfig(BaseModel):
    """Security configuration"""
    secret_key: str = Field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", 
            "your-secret-key-change-this-in-production"
        )
    )
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)


class MonitoringConfig(BaseModel):
    """Monitoring system configuration"""
    # Server settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    
    # Collection intervals
    default_metrics_interval: int = Field(default=60)  # seconds
    default_health_check_interval: int = Field(default=30)  # seconds
    
    # Thresholds
    default_cpu_threshold: float = Field(default=80.0)
    default_memory_threshold: float = Field(default=85.0)
    default_error_rate_threshold: float = Field(default=0.05)
    default_response_time_threshold: float = Field(default=5000.0)  # ms
    
    # Data retention
    metrics_retention_days: int = Field(default=30)
    logs_retention_days: int = Field(default=7)
    
    # System limits
    max_agents: int = Field(default=1000)
    max_concurrent_connections: int = Field(default=100)


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_path: Optional[str] = Field(default_factory=lambda: os.getenv("LOG_FILE"))


class Settings(BaseModel):
    """Main application settings"""
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()