import asyncio
import asyncpg

async def create_db():
    try:
        # Connect to postgres database first
        conn = await asyncpg.connect('postgresql://postgres:admin@host.docker.internal:5432/postgres')
        
        # Check if agent_monitor database exists
        result = await conn.fetch("SELECT 1 FROM pg_database WHERE datname = $1", 'agent_monitor')
        if not result:
            print('Creating agent_monitor database...')
            await conn.execute('CREATE DATABASE agent_monitor')
            print('✅ Database created successfully!')
        else:
            print('✅ Database agent_monitor already exists')
        
        await conn.close()
        
        # Test connection to agent_monitor database
        conn = await asyncpg.connect('postgresql://postgres:admin@host.docker.internal:5432/agent_monitor')
        print('✅ Connection to agent_monitor database successful!')
        await conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    asyncio.run(create_db())