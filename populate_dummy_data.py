#!/usr/bin/env python3
"""
Script to populate the database with dummy agent data for testing the dashboard.
"""
import asyncio
import json
import uuid
from datetime import datetime, timedelta
import random
from typing import List

from sqlalchemy import text
from src.database.connection import db_manager
from src.database.models import Agent, AgentStatus, AgentType, DeploymentType


async def create_dummy_agents() -> List[dict]:
    """Create dummy agent data"""
    agents = [
        {
            "id": str(uuid.uuid4()),
            "name": "Web Server Alpha",
            "type": AgentType.API_AGENT,
            "version": "1.2.3",
            "description": "Main web server handling HTTP requests",
            "deployment_type": DeploymentType.DOCKER,
            "host": "web-01.company.com",
            "port": 8080,
            "environment": "production",
            "status": AgentStatus.ONLINE,
            "agent_metadata": {
                "region": "us-east-1",
                "team": "platform",
                "capabilities": ["http_monitoring", "ssl_check", "performance_tracking"]
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Database Monitor Beta",
            "type": AgentType.MONITOR_AGENT,
            "version": "2.1.0",
            "description": "Database monitoring and performance analysis",
            "deployment_type": DeploymentType.KUBERNETES,
            "host": "db-monitor-01.company.com",
            "port": 5432,
            "environment": "production",
            "status": AgentStatus.ONLINE,
            "agent_metadata": {
                "region": "us-west-2",
                "team": "data",
                "capabilities": ["query_monitoring", "connection_tracking", "performance_analysis"]
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "API Gateway Gamma",
            "type": AgentType.API_AGENT,
            "version": "3.0.1",
            "description": "API gateway handling request routing and auth",
            "deployment_type": DeploymentType.CLOUD,
            "host": "api-01.company.com",
            "port": 443,
            "environment": "production",
            "status": AgentStatus.MAINTENANCE,
            "agent_metadata": {
                "region": "eu-west-1",
                "team": "api",
                "capabilities": ["rate_limiting", "auth_validation", "request_routing"]
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cache Monitor Delta",
            "type": AgentType.MONITOR_AGENT,
            "version": "1.5.2",
            "description": "Redis cache monitoring and optimization",
            "deployment_type": DeploymentType.DOCKER,
            "host": "cache-01.company.com",
            "port": 6379,
            "environment": "staging",
            "status": AgentStatus.ERROR,
            "agent_metadata": {
                "region": "us-east-1",
                "team": "infrastructure",
                "capabilities": ["memory_tracking", "hit_rate_analysis", "eviction_monitoring"]
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Log Processor Epsilon",
            "type": AgentType.DATA_AGENT,
            "version": "4.2.1",
            "description": "Log processing and pattern detection",
            "deployment_type": DeploymentType.KUBERNETES,
            "host": "logs-01.company.com",
            "port": 9200,
            "environment": "production",
            "status": AgentStatus.OFFLINE,
            "agent_metadata": {
                "region": "ap-southeast-1",
                "team": "observability",
                "capabilities": ["log_parsing", "pattern_detection", "alert_generation"]
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Security Scanner Zeta",
            "type": AgentType.MONITOR_AGENT,
            "version": "2.3.0",
            "description": "Security vulnerability scanning and compliance",
            "deployment_type": DeploymentType.CLOUD,
            "host": "security-01.company.com",
            "port": 8443,
            "environment": "production",
            "status": AgentStatus.ONLINE,
            "agent_metadata": {
                "region": "us-west-1",
                "team": "security",
                "capabilities": ["vulnerability_scanning", "threat_detection", "compliance_check"]
            }
        }
    ]
    return agents


def generate_heartbeat_time():
    """Generate a recent heartbeat time"""
    base_time = datetime.utcnow()
    # Random heartbeat within last 30 minutes for online agents
    return base_time - timedelta(minutes=random.randint(0, 30))


async def populate_database():
    """Main function to populate database with dummy data"""
    print("🔄 Starting database population...")
    
    try:
        # Initialize database manager
        await db_manager.initialize()
        
        # Get database session
        async with db_manager.get_async_session() as session:
            print("✅ Database connection established")
            
            # Clear existing agents (optional - comment out to preserve existing data)
            print("🧹 Clearing existing agents...")
            await session.execute(text("DELETE FROM agents"))
            await session.commit()
            
            # Create dummy agents
            print("👥 Creating dummy agents...")
            dummy_agents = await create_dummy_agents()
            
            for agent_data in dummy_agents:
                agent = Agent(
                    id=agent_data["id"],
                    name=agent_data["name"],
                    type=agent_data["type"],
                    version=agent_data["version"],
                    description=agent_data["description"],
                    deployment_type=agent_data["deployment_type"],
                    host=agent_data["host"],
                    port=agent_data["port"],
                    environment=agent_data["environment"],
                    status=agent_data["status"],
                    agent_metadata=agent_data["agent_metadata"],
                    last_heartbeat=generate_heartbeat_time() if agent_data["status"] == AgentStatus.ONLINE else None,
                    last_metrics_received=generate_heartbeat_time() if agent_data["status"] == AgentStatus.ONLINE else None
                )
                session.add(agent)
            
            await session.commit()
            print(f"✅ Created {len(dummy_agents)} agents")            
            print("\n🎉 Database population completed successfully!")
            print(f"📋 Summary:")
            print(f"   - Agents: {len(dummy_agents)}")
            print("   - Note: Metrics and alerts will be simulated via API endpoints")
            
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(populate_database())