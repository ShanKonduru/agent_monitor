import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.connection import DatabaseManager
from src.core.agent_registry import AgentRegistry

async def test_database():
    """Test database connection and data retrieval"""
    print("Testing database connection...")
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        await db_manager.initialize()
        print("✓ Database manager initialized")
        
        # Initialize agent registry
        agent_registry = AgentRegistry(db_manager)
        print("✓ Agent registry initialized")
        
        # Test getting all agents
        agents = await agent_registry.get_all_agents()
        print(f"✓ Retrieved {len(agents)} agents from database")
        
        for i, agent in enumerate(agents):
            print(f"  Agent {i+1}: {agent.id} - {agent.name} ({agent.status})")
            
        # Test get_agent_summary for first agent
        if agents:
            summary = await agent_registry.get_agent_summary(agents[0].id)
            if summary:
                print(f"✓ Agent summary: {summary.name} - {summary.status} - Health: {summary.health_score}")
            else:
                print("✗ Failed to get agent summary")
                
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'db_manager' in locals():
            await db_manager.shutdown()
            print("✓ Database connection closed")

if __name__ == "__main__":
    asyncio.run(test_database())