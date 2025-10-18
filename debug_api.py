import asyncio
import sys
import os
import traceback

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.connection import DatabaseManager
from src.core.agent_registry import AgentRegistry

async def debug_api_issue():
    """Debug the API issue step by step"""
    print("🔍 Debugging API issue...")
    
    try:
        # Step 1: Initialize database manager
        print("\n1. Initializing database manager...")
        db_manager = DatabaseManager()
        await db_manager.initialize()
        print("✅ Database manager initialized")
        
        # Step 2: Initialize agent registry
        print("\n2. Initializing agent registry...")
        agent_registry = AgentRegistry(db_manager)
        print("✅ Agent registry initialized")
        
        # Step 3: Test get_all_agents directly
        print("\n3. Testing get_all_agents()...")
        agents = await agent_registry.get_all_agents()
        print(f"✅ Retrieved {len(agents)} agents")
        
        if agents:
            print("\n📊 Agent Details:")
            for i, agent in enumerate(agents[:3]):  # Show first 3
                print(f"  Agent {i+1}:")
                print(f"    ID: {agent.id}")
                print(f"    Name: {agent.name}")
                print(f"    Type: {agent.type}")
                print(f"    Status: {agent.status}")
                print(f"    Deployment: {agent.deployment_type}")
                print(f"    Last Seen: {agent.last_seen}")
                print(f"    Last Seen Type: {type(agent.last_seen)}")
        
        # Step 4: Test get_agent_summary for first agent
        if agents:
            print(f"\n4. Testing get_agent_summary() for agent: {agents[0].id}")
            summary = await agent_registry.get_agent_summary(agents[0].id)
            if summary:
                print("✅ Agent summary retrieved:")
                print(f"    Name: {summary.name}")
                print(f"    Status: {summary.status}")
                print(f"    Health Score: {summary.health_score}")
                print(f"    Last Seen: {summary.last_seen}")
                print(f"    Last Seen Type: {type(summary.last_seen)}")
            else:
                print("❌ Failed to get agent summary")
        
        # Step 5: Test the API endpoint logic simulation
        print(f"\n5. Simulating API endpoint logic...")
        
        # This simulates what the API endpoint does
        summaries = []
        for agent in agents[:5]:  # Limit to 5 for testing
            try:
                summary = await agent_registry.get_agent_summary(agent.id)
                if summary:
                    summaries.append(summary)
                    print(f"    ✅ Summary for {agent.name}")
                else:
                    print(f"    ❌ No summary for {agent.name}")
            except Exception as e:
                print(f"    💥 Error getting summary for {agent.name}: {e}")
                traceback.print_exc()
        
        print(f"\n✅ API simulation complete: {len(summaries)} summaries created")
        
    except Exception as e:
        print(f"\n💥 Error: {e}")
        traceback.print_exc()
    
    finally:
        if 'db_manager' in locals():
            await db_manager.shutdown()
            print("\n🔒 Database connection closed")

if __name__ == "__main__":
    asyncio.run(debug_api_issue())