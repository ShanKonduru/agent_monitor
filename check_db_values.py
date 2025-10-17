import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.connection import DatabaseManager
from sqlalchemy import text

async def check_db_values():
    """Check actual values in the database"""
    print("Checking database values...")
    
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()
        
        async with db_manager.get_session() as session:
            result = await session.execute(text('SELECT id, name, status, type FROM agents LIMIT 5'))
            rows = result.fetchall()
            
            print("Database values:")
            for row in rows:
                print(f"  ID: {row.id}")
                print(f"  Name: {row.name}")
                print(f"  Status: {row.status} (type: {type(row.status)})")
                print(f"  Type: {row.type} (type: {type(row.type)})")
                print("  ---")
                
        await db_manager.shutdown()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_db_values())