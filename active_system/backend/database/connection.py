"""
Database Connection & Session Management
SQLAlchemy connection pool ve session yönetimi
"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator
import os
from backend.core.settings import settings

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = settings.DATABASE_URL
ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://").replace("postgresql://", "postgresql+asyncpg://")

# Engine configuration
engine_config = {
    "poolclass": QueuePool,
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True,
    "echo": settings.DEBUG,
}

# Sync engine
engine = create_engine(DATABASE_URL, **engine_config)

# Async engine
async_engine = create_async_engine(ASYNC_DATABASE_URL, **engine_config)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=async_engine
)

class DatabaseManager:
    """Database Manager"""
    
    def __init__(self):
        self.engine = engine
        self.async_engine = async_engine
        self.session_local = SessionLocal
        self.async_session_local = AsyncSessionLocal
        logger.info("Database Manager initialized")

    def get_sync_session(self) -> Generator[Session, None, None]:
        """Sync session getter"""
        db = self.session_local()
        try:
            yield db
        finally:
            db.close()

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Async session getter"""
        async with self.async_session_local() as session:
            try:
                yield session
            finally:
                await session.close()

    @contextmanager
    def get_sync_session_context(self) -> Generator[Session, None, None]:
        """Sync session context manager"""
        db = self.session_local()
        try:
            yield db
        except Exception as e:
            db.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            db.close()

    @asynccontextmanager
    async def get_async_session_context(self) -> AsyncGenerator[AsyncSession, None]:
        """Async session context manager"""
        async with self.async_session_local() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Async database session error: {e}")
                raise

    async def health_check(self) -> bool:
        """Database health check"""
        try:
            async with self.get_async_session_context() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def get_connection_info(self) -> dict:
        """Get database connection info"""
        try:
            async with self.get_async_session_context() as session:
                # Get database version
                if "sqlite" in ASYNC_DATABASE_URL:
                    result = await session.execute(text("SELECT sqlite_version()"))
                    version = result.scalar()
                elif "postgresql" in ASYNC_DATABASE_URL:
                    result = await session.execute(text("SELECT version()"))
                    version = result.scalar()
                else:
                    version = "Unknown"
                
                # Get connection pool info
                pool = self.async_engine.pool
                pool_info = {
                    "size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                    "invalid": pool.invalid(),
                }
                
                return {
                    "status": "healthy",
                    "database_url": DATABASE_URL.replace(settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "", "***"),
                    "version": version,
                    "pool_info": pool_info,
                    "timestamp": "2025-09-16T23:45:00Z"
                }
        except Exception as e:
            logger.error(f"Database connection info error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": "2025-09-16T23:45:00Z"
            }

    def close_connections(self):
        """Close all database connections"""
        try:
            self.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

    async def close_async_connections(self):
        """Close all async database connections"""
        try:
            await self.async_engine.dispose()
            logger.info("Async database connections closed")
        except Exception as e:
            logger.error(f"Error closing async database connections: {e}")

# Global database manager instance
db_manager = DatabaseManager()

# Dependency functions for FastAPI
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for sync database session"""
    yield from db_manager.get_sync_session()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database session"""
    async for session in db_manager.get_async_session():
        yield session

# Context managers for manual session management
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for sync database session"""
    yield from db_manager.get_sync_session_context()

async def get_async_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for async database session"""
    async with db_manager.get_async_session_context() as session:
        yield session

# Database initialization
async def init_database():
    """Initialize database tables"""
    try:
        from backend.models.database import Base
        
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

# Database cleanup
async def cleanup_database():
    """Cleanup database connections"""
    try:
        await db_manager.close_async_connections()
        db_manager.close_connections()
        logger.info("Database cleanup completed")
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")

# Health check endpoint
async def database_health_check() -> dict:
    """Database health check for API endpoint"""
    try:
        is_healthy = await db_manager.health_check()
        connection_info = await db_manager.get_connection_info()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "database_health": is_healthy,
            "connection_info": connection_info,
            "timestamp": "2025-09-16T23:45:00Z"
        }
    except Exception as e:
        logger.error(f"Database health check endpoint error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-09-16T23:45:00Z"
        }
