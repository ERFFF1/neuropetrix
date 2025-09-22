"""
Connection Pool Manager
Veritabanı ve HTTP bağlantı havuzu yönetimi
"""

import asyncio
import aiohttp
import asyncpg
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@dataclass
class PoolConfig:
    """Bağlantı havuzu konfigürasyonu"""
    min_connections: int = 5
    max_connections: int = 20
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

class DatabasePool:
    """Veritabanı bağlantı havuzu"""
    
    def __init__(self, config: PoolConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
        self._lock = asyncio.Lock()
    
    async def initialize(self, database_url: str):
        """Havuzu başlat"""
        try:
            async with self._lock:
                if self.pool is None:
                    self.pool = await asyncpg.create_pool(
                        database_url,
                        min_size=self.config.min_connections,
                        max_size=self.config.max_connections,
                        command_timeout=self.config.timeout
                    )
                    logger.info(f"Database pool initialized: {self.config.min_connections}-{self.config.max_connections} connections")
        except Exception as e:
            logger.error(f"Database pool initialization failed: {e}")
            raise
    
    async def close(self):
        """Havuzu kapat"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def acquire(self):
        """Bağlantı al"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        connection = None
        try:
            connection = await self.pool.acquire()
            yield connection
        finally:
            if connection:
                await self.pool.release(connection)
    
    async def execute(self, query: str, *args):
        """Query çalıştır"""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Query sonuçlarını getir"""
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Tek satır getir"""
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    def get_stats(self) -> Dict[str, Any]:
        """Havuz istatistikleri"""
        if not self.pool:
            return {"status": "not_initialized"}
        
        return {
            "status": "active",
            "size": self.pool.get_size(),
            "min_size": self.pool.get_min_size(),
            "max_size": self.pool.get_max_size(),
            "idle_connections": self.pool.get_idle_size(),
            "used_connections": self.pool.get_size() - self.pool.get_idle_size()
        }

class HTTPPool:
    """HTTP bağlantı havuzu"""
    
    def __init__(self, config: PoolConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Session başlat"""
        try:
            async with self._lock:
                if self.session is None:
                    connector = aiohttp.TCPConnector(
                        limit=self.config.max_connections,
                        limit_per_host=self.config.max_connections // 2,
                        ttl_dns_cache=300,
                        use_dns_cache=True,
                    )
                    
                    timeout = aiohttp.ClientTimeout(total=self.config.timeout)
                    
                    self.session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=timeout
                    )
                    logger.info(f"HTTP session initialized: {self.config.max_connections} max connections")
        except Exception as e:
            logger.error(f"HTTP session initialization failed: {e}")
            raise
    
    async def close(self):
        """Session kapat"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("HTTP session closed")
    
    async def get(self, url: str, **kwargs):
        """GET request"""
        if not self.session:
            raise RuntimeError("HTTP session not initialized")
        
        for attempt in range(self.config.retry_attempts):
            try:
                async with self.session.get(url, **kwargs) as response:
                    return response
            except Exception as e:
                if attempt == self.config.retry_attempts - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
    
    async def post(self, url: str, **kwargs):
        """POST request"""
        if not self.session:
            raise RuntimeError("HTTP session not initialized")
        
        for attempt in range(self.config.retry_attempts):
            try:
                async with self.session.post(url, **kwargs) as response:
                    return response
            except Exception as e:
                if attempt == self.config.retry_attempts - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
    
    def get_stats(self) -> Dict[str, Any]:
        """Session istatistikleri"""
        if not self.session:
            return {"status": "not_initialized"}
        
        connector = self.session.connector
        return {
            "status": "active",
            "max_connections": connector.limit,
            "max_per_host": connector.limit_per_host,
            "dns_cache_size": len(connector._dns_cache) if hasattr(connector, '_dns_cache') else 0,
            "closed": connector.closed
        }

class ConnectionPoolManager:
    """Bağlantı havuzu yöneticisi"""
    
    def __init__(self):
        self.db_pools: Dict[str, DatabasePool] = {}
        self.http_pools: Dict[str, HTTPPool] = {}
        self._initialized = False
    
    async def initialize(self):
        """Tüm havuzları başlat"""
        try:
            # Database pools
            db_config = PoolConfig(min_connections=5, max_connections=20)
            self.db_pools["main"] = DatabasePool(db_config)
            
            # HTTP pools
            http_config = PoolConfig(min_connections=10, max_connections=50)
            self.http_pools["main"] = HTTPPool(http_config)
            await self.http_pools["main"].initialize()
            
            self._initialized = True
            logger.info("Connection pool manager initialized")
            
        except Exception as e:
            logger.error(f"Connection pool manager initialization failed: {e}")
            raise
    
    async def close_all(self):
        """Tüm havuzları kapat"""
        try:
            # Close database pools
            for pool in self.db_pools.values():
                await pool.close()
            
            # Close HTTP pools
            for pool in self.http_pools.values():
                await pool.close()
            
            self._initialized = False
            logger.info("All connection pools closed")
            
        except Exception as e:
            logger.error(f"Error closing connection pools: {e}")
    
    def get_db_pool(self, name: str = "main") -> Optional[DatabasePool]:
        """Database pool getir"""
        return self.db_pools.get(name)
    
    def get_http_pool(self, name: str = "main") -> Optional[HTTPPool]:
        """HTTP pool getir"""
        return self.http_pools.get(name)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Tüm havuz istatistikleri"""
        return {
            "initialized": self._initialized,
            "database_pools": {
                name: pool.get_stats() for name, pool in self.db_pools.items()
            },
            "http_pools": {
                name: pool.get_stats() for name, pool in self.http_pools.items()
            }
        }

# Global instance
connection_pool_manager = ConnectionPoolManager()
