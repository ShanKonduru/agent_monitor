#!/usr/bin/env python3
"""
Simple test to check if agents were inserted and can be retrieved from database.
"""
import asyncio
from sqlalchemy import select
from src.database.connection import db_manager
from src.database.models import Agent

async def test_agents():
    """Test retrieving agents from database"""
    try:
        # Initialize database manager
        await db_manager.initialize()
        
        # Get database session
        async with db_manager.get_async_session() as session:
            print("✅ Database connection established")
            
            # Query all agents using SQLAlchemy ORM
            result = await session.execute(select(Agent))
            agents = result.scalars().all()
            
            print(f"📊 Found {len(agents)} agents in database:")
            for agent in agents:
                print(f"  - {agent.name} ({agent.status.value}) - {agent.host}:{agent.port}")
                print(f"    Type: {agent.type.value}, Environment: {agent.environment}")
                print(f"    Last heartbeat: {agent.last_heartbeat}")
                print()
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agents())