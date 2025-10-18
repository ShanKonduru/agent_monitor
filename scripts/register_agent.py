import asyncio
import sys
import os

# Add src to path - go up one directory first
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models import AgentInfo, AgentType, DeploymentType
from src.database.connection import DatabaseManager
from src.core.agent_registry import AgentRegistry

async def register_agent(name, agent_type="API_AGENT", host="localhost", environment="development"):
    """Register a new agent"""
    try:
        agent_info = AgentInfo(
            name=name,
            type=agent_type,
            version="1.0.0",
            deployment_type="LOCAL",
            host=host,
            environment=environment,
            description=f"Agent registered via batch script"
        )
        
        db_manager = DatabaseManager()
        await db_manager.initialize()
        registry = AgentRegistry(db_manager)
        response = await registry.register_agent(agent_info)
        
        print(f"✅ Agent registered successfully!")
        print(f"   ID: {response.agent_id}")
        print(f"   Name: {name}")
        print(f"   Type: {agent_type}")
        print(f"   Status: {response.status}")
        
        await db_manager.shutdown()
        
    except Exception as e:
        print(f"❌ Error registering agent: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python register_agent.py <name> [type] [host] [environment]")
        print("Example: python register_agent.py 'My Agent' API_AGENT localhost production")
        sys.exit(1)
    
    name = sys.argv[1]
    agent_type = sys.argv[2] if len(sys.argv) > 2 else "API_AGENT"
    host = sys.argv[3] if len(sys.argv) > 3 else "localhost" 
    environment = sys.argv[4] if len(sys.argv) > 4 else "development"
    
    asyncio.run(register_agent(name, agent_type, host, environment))