"""""""""

Database connection and session management for the Agent Monitor Framework.

"""Database connection and session management for the Agent Monitor Framework.Database connection and session management for the Agent Monitor Framework.



import os""""""

import logging

from typing import Generator, Optional

from contextlib import asynccontextmanager

import osimport os

from sqlalchemy import create_engine, MetaData, text

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmakerimport loggingimport logging

from sqlalchemy.orm import sessionmaker, Session

import redis.asyncio as redisfrom typing import Generator, Optionalfrom typing import Generator, Optional



# Optional InfluxDB importfrom contextlib import asynccontextmanagerfrom contextlib import asynccontextmanager

try:

    from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

    INFLUXDB_AVAILABLE = True

except ImportError:from sqlalchemy import create_engine, MetaData, textfrom sqlalchemy import create_engine, MetaData, text

    InfluxDBClientAsync = None

    INFLUXDB_AVAILABLE = Falsefrom sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmakerfrom sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker



from src.config import settingsfrom sqlalchemy.orm import sessionmaker, Sessionfrom sqlalchemy.orm import sessionmaker, Session

from src.database.models import Base

from sqlalchemy.pool import StaticPoolfrom sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

import redis.asyncio as redisimport redis.asyncio as redis



class DatabaseManager:

    """Manages database connections and sessions"""

    # Optional InfluxDB import# Optional InfluxDB import

    def __init__(self):

        self.postgres_engine = Nonetry:try:

        self.async_postgres_engine = None

        self.session_factory = None    from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync    from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

        self.async_session_factory = None

        self.redis_client = None    INFLUXDB_AVAILABLE = True    INFLUXDB_AVAILABLE = True

        self.influx_client = None

        except ImportError:except ImportError:

    async def initialize(self):

        """Initialize all database connections"""    InfluxDBClientAsync = None    InfluxDBClientAsync = None

        await self._setup_postgresql()

        await self._setup_redis()    INFLUXDB_AVAILABLE = False    INFLUXDB_AVAILABLE = False

        await self._setup_influxdb()

        

    async def _setup_postgresql(self):

        """Setup PostgreSQL connections"""from src.config import settingsfrom src.config import settings

        try:

            # Create async engine for PostgreSQLfrom src.database.models import Basefrom src.database.models import Base

            self.async_postgres_engine = create_async_engine(

                settings.database.url,

                echo=settings.database.echo,

                pool_size=settings.database.pool_size,logger = logging.getLogger(__name__)logger = logging.getLogger(__name__)

                max_overflow=settings.database.max_overflow,

                pool_pre_ping=True,

                pool_recycle=3600,  # Recycle connections every hour

            )

            

            # Create session factoryclass DatabaseManager:class DatabaseManager:

            self.async_session_factory = async_sessionmaker(

                self.async_postgres_engine,    """Manages database connections and sessions"""    """Simple mock session for in-memory database"""

                class_=AsyncSession,

                expire_on_commit=False        

            )

                def __init__(self):    def __init__(self, memory_store):

            # Create tables if they don't exist

            async with self.async_postgres_engine.begin() as conn:        self.postgres_engine = None        self.memory_store = memory_store

                await conn.run_sync(Base.metadata.create_all)

                        self.async_postgres_engine = None        self._pending_objects = []

            logger.info("PostgreSQL connection established successfully")

                    self.session_factory = None        

        except Exception as e:

            logger.error(f"Failed to setup PostgreSQL: {e}")        self.async_session_factory = None    def add(self, obj):

            raise

            self.redis_client = None        """Add object to pending list for commit"""

    async def _setup_redis(self):

        """Setup Redis connection for caching"""        self.influx_client = None        self._pending_objects.append(obj)

        if not settings.redis.url:

            logger.info("Redis URL not configured, skipping Redis setup")                    

            return

                async def initialize(self):    async def commit(self):

        try:

            self.redis_client = redis.from_url(        """Initialize all database connections"""        """Commit pending objects to memory store"""

                settings.redis.url,

                encoding="utf-8",        await self._setup_postgresql()        for obj in self._pending_objects:

                decode_responses=True,

                socket_connect_timeout=settings.redis.timeout,        await self._setup_redis()            if hasattr(obj, 'id'):

                socket_timeout=settings.redis.timeout,

            )        await self._setup_influxdb()                table_name = obj.__class__.__name__.lower() + 's'

            

            # Test the connection                        if table_name not in self.memory_store:

            await self.redis_client.ping()

            logger.info("Redis connection established successfully")    async def _setup_postgresql(self):                    self.memory_store[table_name] = {}

            

        except Exception as e:        """Setup PostgreSQL connections"""                # Store the object itself to preserve all attributes

            logger.warning(f"Failed to setup Redis: {e}")

            self.redis_client = None        try:                self.memory_store[table_name][obj.id] = obj

    

    async def _setup_influxdb(self):            # Create async engine        self._pending_objects.clear()

        """Setup InfluxDB connection for time-series data"""

        if not INFLUXDB_AVAILABLE or not settings.influxdb.url:            self.async_postgres_engine = create_async_engine(        

            logger.info("InfluxDB not available or not configured, skipping setup")

            return                settings.database.url,    async def rollback(self):

            

        try:                echo=settings.database.echo,        """Mock rollback - clear pending objects"""

            self.influx_client = InfluxDBClientAsync(

                url=settings.influxdb.url,                pool_size=settings.database.pool_size,        self._pending_objects.clear()

                token=settings.influxdb.token,

                org=settings.influxdb.org,                max_overflow=settings.database.max_overflow,        

                timeout=settings.influxdb.timeout * 1000,  # Convert to milliseconds

            )                pool_pre_ping=True,    async def execute(self, query):

            

            # Test the connection                pool_recycle=3600,  # Recycle connections every hour        """Mock execute - return agents data based on query"""

            health = await self.influx_client.health()

            if health.status == "pass":            )        # Simple query handling - if it's asking for agents, return them

                logger.info("InfluxDB connection established successfully")

            else:                    query_str = str(query).lower()

                logger.warning(f"InfluxDB health check failed: {health.message}")

                            # Create session factory        if 'agent' in query_str or 'select' in query_str:

        except Exception as e:

            logger.warning(f"Failed to setup InfluxDB: {e}")            self.async_session_factory = async_sessionmaker(            agents_data = self.memory_store.get('agents', {})

            self.influx_client = None

                    self.async_postgres_engine,            agents_list = list(agents_data.values())

    @asynccontextmanager

    async def get_session(self) -> AsyncSession:                class_=AsyncSession,            # Check if it's a specific agent query (WHERE clause)

        """Get async database session with automatic cleanup"""

        if not self.async_session_factory:                expire_on_commit=False            if 'where' in query_str and len(agents_list) > 0:

            raise RuntimeError("Database not initialized. Call initialize() first.")

                        )                # For single agent queries, return just one agent

        async with self.async_session_factory() as session:

            try:                            return MockResult([agents_list[0]])

                yield session

            except Exception:            # Create sync engine for initial setup            return MockResult(agents_list)

                await session.rollback()

                raise            sync_url = settings.database.url.replace('+asyncpg', '')        return MockResult([])

            finally:

                await session.close()            self.postgres_engine = create_engine(sync_url)        

    

    @asynccontextmanager                async def refresh(self, obj):

    async def get_redis(self):

        """Get Redis client"""            # Create tables if they don't exist        """Mock refresh - no-op but don't error"""

        if not self.redis_client:

            raise RuntimeError("Redis not initialized or not available")            async with self.async_postgres_engine.begin() as conn:        pass

        yield self.redis_client

                    await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager

    async def get_influx(self):                

        """Get InfluxDB client"""

        if not self.influx_client:            logger.info("PostgreSQL connection established successfully")class MockResult:

            raise RuntimeError("InfluxDB not initialized or not available")

        yield self.influx_client                """Mock query result"""

    

    async def health_check(self) -> dict:        except Exception as e:    

        """Check health of all database connections"""

        health = {}            logger.error(f"Failed to setup PostgreSQL: {e}")    def __init__(self, data):

        

        # Check PostgreSQL            raise        self.data = data

        try:

            async with self.get_session() as session:            

                result = await session.execute(text("SELECT 1"))

                health['postgresql'] = {'status': 'healthy', 'latency_ms': None}    async def _setup_redis(self):    def scalars(self):

        except Exception as e:

            health['postgresql'] = {'status': 'unhealthy', 'error': str(e)}        """Setup Redis connection for caching"""        return MockScalar(self.data)

        

        # Check Redis        if not settings.redis.url:        

        if self.redis_client:

            try:            logger.info("Redis URL not configured, skipping Redis setup")    def all(self):

                await self.redis_client.ping()

                health['redis'] = {'status': 'healthy'}            return        return self.data

            except Exception as e:

                health['redis'] = {'status': 'unhealthy', 'error': str(e)}                    

        else:

            health['redis'] = {'status': 'not_configured'}        try:    def scalar_one_or_none(self):

        

        # Check InfluxDB            self.redis_client = redis.from_url(        """Return first item or None"""

        if self.influx_client:

            try:                settings.redis.url,        return self.data[0] if self.data else None

                influx_health = await self.influx_client.health()

                health['influxdb'] = {                encoding="utf-8",

                    'status': 'healthy' if influx_health.status == 'pass' else 'unhealthy',

                    'message': influx_health.message                decode_responses=True,

                }

            except Exception as e:                socket_connect_timeout=settings.redis.timeout,class MockScalar:

                health['influxdb'] = {'status': 'unhealthy', 'error': str(e)}

        else:                socket_timeout=settings.redis.timeout,    """Mock scalar result"""

            health['influxdb'] = {'status': 'not_configured'}

                    )    

        return health

                    def __init__(self, data):

    async def close(self):

        """Close all database connections"""            # Test the connection        self.data = data

        if self.async_postgres_engine:

            await self.async_postgres_engine.dispose()            await self.redis_client.ping()        

        

        if self.postgres_engine:            logger.info("Redis connection established successfully")    def all(self):

            self.postgres_engine.dispose()

                            # Return the actual objects, not wrapped in MockAgent

        if self.redis_client:

            await self.redis_client.close()        except Exception as e:        return self.data if self.data else []

        

        if self.influx_client:            logger.warning(f"Failed to setup Redis: {e}")        

            await self.influx_client.close()

                    self.redis_client = None    def first(self):

        logger.info("All database connections closed")

            """Return first item or None"""



# Global database manager instance    async def _setup_influxdb(self):        return self.data[0] if self.data else None

db_manager = DatabaseManager()

        """Setup InfluxDB connection for time-series data"""



async def get_database_session() -> Generator[AsyncSession, None, None]:        if not INFLUXDB_AVAILABLE or not settings.influxdb.url:

    """Dependency function for FastAPI to get database session"""

    async with db_manager.get_session() as session:            logger.info("InfluxDB not available or not configured, skipping setup")class DatabaseManager:

        yield session

            return    """Manages database connections and sessions"""



async def get_redis_client():                

    """Dependency function for FastAPI to get Redis client"""

    async with db_manager.get_redis() as redis_client:        try:    def __init__(self):

        yield redis_client

            self.influx_client = InfluxDBClientAsync(        self.postgres_engine = None



async def get_influx_client():                url=settings.influxdb.url,        self.async_postgres_engine = None

    """Dependency function for FastAPI to get InfluxDB client"""

    async with db_manager.get_influx() as influx_client:                token=settings.influxdb.token,        self.session_factory = None

        yield influx_client

                org=settings.influxdb.org,        self.async_session_factory = None



# Helper functions for backward compatibility                timeout=settings.influxdb.timeout * 1000,  # Convert to milliseconds        self.redis_client = None

async def init_database():

    """Initialize the database connection"""            )        self.influx_client = None

    await db_manager.initialize()

                    



async def close_database():            # Test the connection    async def initialize(self):

    """Close the database connection"""

    await db_manager.close()            health = await self.influx_client.health()        """Initialize all database connections"""



            if health.status == "pass":        await self._setup_postgresql()

async def get_db_session():

    """Get a database session (async context manager)"""                logger.info("InfluxDB connection established successfully")        await self._setup_redis()

    return db_manager.get_session()
            else:        await self._setup_influxdb()

                logger.warning(f"InfluxDB health check failed: {health.message}")        

                    async def shutdown(self):

        except Exception as e:        """Cleanup database connections"""

            logger.warning(f"Failed to setup InfluxDB: {e}")        if self.postgres_engine:

            self.influx_client = None            self.postgres_engine.dispose()

                

    @asynccontextmanager        if self.async_postgres_engine:

    async def get_session(self) -> AsyncSession:            await self.async_postgres_engine.dispose()

        """Get async database session with automatic cleanup"""            

        if not self.async_session_factory:        if self.redis_client:

            raise RuntimeError("Database not initialized. Call initialize() first.")            await self.redis_client.close()

                        

        async with self.async_session_factory() as session:        if self.influx_client:

            try:            await self.influx_client.close()

                yield session            

            except Exception:    async def _setup_postgresql(self):

                await session.rollback()        """Setup database connection"""

                raise        try:

            finally:            if settings.database.postgres_url.startswith("memory://"):

                await session.close()                # In-memory database for demo purposes

                    logger.info("Using in-memory database for demonstration")

    @asynccontextmanager                self.postgres_engine = None

    async def get_redis(self):                self.async_postgres_engine = None

        """Get Redis client"""                self.session_factory = None

        if not self.redis_client:                self.async_session_factory = None

            raise RuntimeError("Redis not initialized or not available")                # We'll use a simple in-memory store

        yield self.redis_client                self._memory_store = {}

                    logger.info("In-memory database initialized")

    @asynccontextmanager                return

    async def get_influx(self):                

        """Get InfluxDB client"""            # PostgreSQL configuration

        if not self.influx_client:            self.postgres_engine = create_engine(

            raise RuntimeError("InfluxDB not initialized or not available")                settings.database.postgres_url,

        yield self.influx_client                pool_pre_ping=True,

                    pool_recycle=3600,

    async def health_check(self) -> dict:                echo=settings.logging.level == "DEBUG"

        """Check health of all database connections"""            )

        health = {}            

                    # Create async engine for application use

        # Check PostgreSQL            # Convert postgres:// to postgresql+asyncpg://

        try:            async_url = settings.database.postgres_url.replace(

            async with self.get_session() as session:                "postgresql://", "postgresql+asyncpg://"

                result = await session.execute(text("SELECT 1"))            ).replace("postgres://", "postgresql+asyncpg://")

                health['postgresql'] = {'status': 'healthy', 'latency_ms': None}            

        except Exception as e:            self.async_postgres_engine = create_async_engine(

            health['postgresql'] = {'status': 'unhealthy', 'error': str(e)}                async_url,

                        pool_pre_ping=True,

        # Check Redis                pool_recycle=3600,

        if self.redis_client:                echo=settings.logging.level == "DEBUG"

            try:            )

                await self.redis_client.ping()            

                health['redis'] = {'status': 'healthy'}            # Create session factories

            except Exception as e:            self.session_factory = sessionmaker(

                health['redis'] = {'status': 'unhealthy', 'error': str(e)}                bind=self.postgres_engine,

        else:                autocommit=False,

            health['redis'] = {'status': 'not_configured'}                autoflush=False

                    )

        # Check InfluxDB            

        if self.influx_client:            self.async_session_factory = async_sessionmaker(

            try:                bind=self.async_postgres_engine,

                influx_health = await self.influx_client.health()                class_=AsyncSession,

                health['influxdb'] = {                autocommit=False,

                    'status': 'healthy' if influx_health.status == 'pass' else 'unhealthy',                autoflush=False,

                    'message': influx_health.message                expire_on_commit=False

                }            )

            except Exception as e:        

                health['influxdb'] = {'status': 'unhealthy', 'error': str(e)}            logger.info(f"Database connection initialized: {settings.database.postgres_url.split('://')[0]}")

        else:            

            health['influxdb'] = {'status': 'not_configured'}        except Exception as e:

                    logger.error(f"Failed to initialize database: {e}")

        return health            raise

                

    async def close(self):    async def _setup_redis(self):

        """Close all database connections"""        """Setup Redis connection"""

        if self.async_postgres_engine:        try:

            await self.async_postgres_engine.dispose()            self.redis_client = redis.from_url(

                        settings.redis.redis_url,

        if self.postgres_engine:                password=settings.redis.redis_password,

            self.postgres_engine.dispose()                decode_responses=True,

                        retry_on_timeout=True,

        if self.redis_client:                health_check_interval=30

            await self.redis_client.close()            )

                    

        if self.influx_client:            # Test connection

            await self.influx_client.close()            await self.redis_client.ping()

                    logger.info("Redis connection initialized")

        logger.info("All database connections closed")            

        except Exception as e:

            logger.error(f"Failed to initialize Redis: {e}")

# Global database manager instance            # Don't raise - Redis is optional for basic functionality

db_manager = DatabaseManager()            self.redis_client = None

            

    async def _setup_influxdb(self):

async def get_database_session() -> Generator[AsyncSession, None, None]:        """Setup InfluxDB connection"""

    """Dependency function for FastAPI to get database session"""        try:

    async with db_manager.get_session() as session:            if not INFLUXDB_AVAILABLE:

        yield session                logger.warning("InfluxDB client not available - skipping InfluxDB setup")

                self.influx_client = None

                return

async def get_redis_client():                

    """Dependency function for FastAPI to get Redis client"""            self.influx_client = InfluxDBClientAsync(

    async with db_manager.get_redis() as redis_client:                url=settings.database.influxdb_url,

        yield redis_client                token=settings.database.influxdb_token,

                org=settings.database.influxdb_org,

                timeout=10000

async def get_influx_client():            )

    """Dependency function for FastAPI to get InfluxDB client"""            

    async with db_manager.get_influx() as influx_client:            # Test connection

        yield influx_client            await self.influx_client.ping()

            logger.info("InfluxDB connection initialized")

            

# Helper functions for backward compatibility        except Exception as e:

async def init_database():            logger.error(f"Failed to initialize InfluxDB: {e}")

    """Initialize the database connection"""            # Don't raise - InfluxDB is optional for basic functionality

    await db_manager.initialize()            self.influx_client = None

    

    def get_sync_session(self) -> Session:

async def close_database():        """Get synchronous database session"""

    """Close the database connection"""        if not self.session_factory:

    await db_manager.close()            raise RuntimeError("Database not initialized")

        return self.session_factory()

    

async def get_db_session():    @asynccontextmanager

    """Get a database session (async context manager)"""    async def get_session(self):

    return db_manager.get_session()        """Get database session context manager (alias for get_async_session)"""
        async with self.get_async_session() as session:
            yield session

    @asynccontextmanager
    async def get_async_session(self):
        """Get asynchronous database session context manager"""
        if hasattr(self, '_memory_store'):
            # For in-memory database, yield a mock session
            yield MockSession(self._memory_store)
            return
            
        if not self.async_session_factory:
            raise RuntimeError("Database not initialized")
            
        # Use PostgreSQL async session
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def get_redis(self) -> Optional[redis.Redis]:
        """Get Redis client"""
        return self.redis_client
    
    async def get_influx(self):
        """Get InfluxDB client"""
        return self.influx_client
    
    async def create_tables(self):
        """Create database tables"""
        if hasattr(self, '_memory_store'):
            # For in-memory database, initialize basic structure
            self._memory_store['agents'] = {}
            logger.info("In-memory database tables initialized")
            return
            
        # Use PostgreSQL async table creation
        if not self.async_postgres_engine:
            raise RuntimeError("PostgreSQL not initialized")
            
        async with self.async_postgres_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created")
    
    async def health_check(self) -> dict:
        """Check health of all database connections"""
        health = {
            "postgresql": False,
            "redis": False,
            "influxdb": False
        }
        
        # Check database
        try:
            if hasattr(self, '_memory_store'):
                # For in-memory database, always healthy
                health["postgresql"] = True
            else:
                # For PostgreSQL, use async query
                async with self.get_async_session() as session:
                    await session.execute(text("SELECT 1"))
                    health["postgresql"] = True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
        
        # Check Redis
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health["redis"] = True
            except Exception as e:
                logger.error(f"Redis health check failed: {e}")
        
        # Check InfluxDB
        if self.influx_client:
            try:
                await self.influx_client.ping()
                health["influxdb"] = True
            except Exception as e:
                logger.error(f"InfluxDB health check failed: {e}")
        
        return health


# Global database manager instance
db_manager = DatabaseManager()


# Dependency functions for FastAPI
async def get_db_session():
    """FastAPI dependency for database session"""
    async with db_manager.get_async_session() as session:
        yield session


async def get_redis_client() -> Optional[redis.Redis]:
    """FastAPI dependency for Redis client"""
    return await db_manager.get_redis()


async def get_influx_client():
    """FastAPI dependency for InfluxDB client"""
    return await db_manager.get_influx()


# Utility functions
async def init_database():
    """Initialize database with tables and default data"""
    await db_manager.initialize()
    await db_manager.create_tables()
    logger.info("Database initialization complete")


async def cleanup_database():
    """Cleanup database connections"""
    await db_manager.shutdown()
    logger.info("Database cleanup complete")


class DatabaseError(Exception):
    """Base database error"""
    pass


class ConnectionError(DatabaseError):
    """Database connection error"""
    pass


class QueryError(DatabaseError):
    """Database query error"""
    pass