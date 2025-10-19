"""
Docker configuration settings
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DockerSettings:
    """Simplified settings for Docker environment"""
    
    # Database
    database_url: str = "sqlite:///./data/agent_monitor.db"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    
    # Features (disabled for Docker simplicity)
    enable_redis: bool = False
    enable_influxdb: bool = False
    enable_auth: bool = False
    
    def __post_init__(self):
        # Override with environment variables if available
        self.database_url = os.getenv("DATABASE_URL", self.database_url)
        self.host = os.getenv("HOST", self.host)
        self.port = int(os.getenv("PORT", self.port))
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)

# Global settings instance
docker_settings = DockerSettings()