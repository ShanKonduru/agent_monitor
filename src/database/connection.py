"""
Database connection and session management for the Agent Monitor Framework.
"""

import os
import logging
from typing import Generator, Optional
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import redis.asyncio as redis
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from src.config import settings
from src.database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self):
        self.postgres_engine = None
        self.async_postgres_engine = None
        self.session_factory = None
        self.async_session_factory = None
        self.redis_client = None
        self.influx_client = None
        
    async def initialize(self):
        """Initialize all database connections"""
        await self._setup_postgresql()
        await self._setup_redis()
        await self._setup_influxdb()
        
    async def shutdown(self):
        """Cleanup database connections"""
        if self.postgres_engine:
            self.postgres_engine.dispose()
            
        if self.async_postgres_engine:
            await self.async_postgres_engine.dispose()
            
        if self.redis_client:
            await self.redis_client.close()
            
        if self.influx_client:
            await self.influx_client.close()
            
    async def _setup_postgresql(self):
        """Setup PostgreSQL/SQLite connection"""
        try:
            # Create synchronous engine for migrations
            if settings.database.postgres_url.startswith("sqlite"):
                # SQLite configuration
                self.postgres_engine = create_engine(
                    settings.database.postgres_url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=settings.logging.level == "DEBUG"
                )
                # SQLite doesn't support async, use sync for both
                async_url = settings.database.postgres_url
                self.async_postgres_engine = create_engine(
                    async_url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=settings.logging.level == "DEBUG"
                )
                
                # Use sync sessions for SQLite
                self.session_factory = sessionmaker(
                    bind=self.postgres_engine,
                    autocommit=False,
                    autoflush=False
                )
                
                # For SQLite, use sync session wrapped as async
                self.async_session_factory = sessionmaker(
                    bind=self.async_postgres_engine,
                    autocommit=False,
                    autoflush=False
                )
                
            else:
                # PostgreSQL configuration
                self.postgres_engine = create_engine(
                    settings.database.postgres_url,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=settings.logging.level == "DEBUG"
                )
                
                # Create async engine for application use
                # Convert postgres:// to postgresql+asyncpg://
                async_url = settings.database.postgres_url.replace(
                    "postgresql://", "postgresql+asyncpg://"
                ).replace("postgres://", "postgresql+asyncpg://")
                
                self.async_postgres_engine = create_async_engine(
                    async_url,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=settings.logging.level == "DEBUG"
                )
                
                # Create session factories
                self.session_factory = sessionmaker(
                    bind=self.postgres_engine,
                    autocommit=False,
                    autoflush=False
                )
                
                self.async_session_factory = async_sessionmaker(
                    bind=self.async_postgres_engine,
                    class_=AsyncSession,
                    autocommit=False,
                    autoflush=False,
                    expire_on_commit=False
                )
            
            logger.info(f"Database connection initialized: {settings.database.postgres_url.split('://')[0]}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
            
    async def _setup_redis(self):
        """Setup Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.redis.redis_url,
                password=settings.redis.redis_password,
                decode_responses=True,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            # Don't raise - Redis is optional for basic functionality
            self.redis_client = None
            
    async def _setup_influxdb(self):
        """Setup InfluxDB connection"""
        try:
            self.influx_client = InfluxDBClientAsync(
                url=settings.database.influxdb_url,
                token=settings.database.influxdb_token,
                org=settings.database.influxdb_org,
                timeout=10000
            )
            
            # Test connection
            await self.influx_client.ping()
            logger.info("InfluxDB connection initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize InfluxDB: {e}")
            # Don't raise - InfluxDB is optional for basic functionality
            self.influx_client = None
    
    def get_sync_session(self) -> Session:
        """Get synchronous database session"""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        return self.session_factory()
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session context manager (alias for get_async_session)"""
        async with self.get_async_session() as session:
            yield session

    @asynccontextmanager
    async def get_async_session(self):
        """Get asynchronous database session context manager"""
        if not self.async_session_factory:
            raise RuntimeError("Database not initialized")
            
        if settings.database.postgres_url.startswith("sqlite"):
            # For SQLite, use sync session
            session = self.async_session_factory()
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        else:
            # For PostgreSQL, use async session
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
    
    async def get_influx(self) -> Optional[InfluxDBClientAsync]:
        """Get InfluxDB client"""
        return self.influx_client
    
    async def create_tables(self):
        """Create database tables"""
        if settings.database.postgres_url.startswith("sqlite"):
            # For SQLite, use sync table creation
            Base.metadata.create_all(bind=self.postgres_engine)
        else:
            # For PostgreSQL, use async table creation
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
        
        # Check PostgreSQL/SQLite
        try:
            if settings.database.postgres_url.startswith("sqlite"):
                # For SQLite, use sync query
                session = self.session_factory()
                try:
                    session.execute(text("SELECT 1"))
                    health["postgresql"] = True
                finally:
                    session.close()
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


async def get_influx_client() -> Optional[InfluxDBClientAsync]:
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