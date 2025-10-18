"""
Simple database connection for local development.
"""

import os
import logging
from typing import Generator, Optional
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session

from src.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Simplified database manager for local development"""
    
    def __init__(self):
        self.async_engine = None
        self.async_session_factory = None
        self.sync_engine = None
        self.sync_session_factory = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connections"""
        if self._initialized:
            return
            
        try:
            # For local development, use a simpler database URL
            database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:G@ll0p123$@localhost:5432/postgres")
            
            # Create async engine
            self.async_engine = create_async_engine(
                database_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Create session factory
            self.async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            self._initialized = True
            logger.info("Database manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            # For development, we can continue without database
            self._initialized = True
    
    @asynccontextmanager
    async def get_session(self) -> Generator[AsyncSession, None, None]:
        """Get database session"""
        if not self._initialized:
            await self.initialize()
            
        if not self.async_session_factory:
            # Mock session for development
            class MockSession:
                async def commit(self): pass
                async def rollback(self): pass
                async def close(self): pass
                def add(self, obj): pass
                async def execute(self, query): 
                    class MockResult:
                        def scalars(self): 
                            class MockScalars:
                                def all(self): return []
                                def first(self): return None
                            return MockScalars()
                    return MockResult()
            
            yield MockSession()
            return
            
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            if not self.async_engine:
                return False
                
            async with self.async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()