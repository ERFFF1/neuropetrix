import asyncio
import aiohttp
import time
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"
    HEALTH_BASED = "health_based"

@dataclass
class Server:
    url: str
    weight: int = 1
    max_connections: int = 100
    current_connections: int = 0
    response_time: float = 0.0
    is_healthy: bool = True
    last_health_check: float = 0.0
    error_count: int = 0
    success_count: int = 0

class LoadBalancer:
    """Advanced load balancer with multiple strategies."""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN):
        self.servers: List[Server] = []
        self.strategy = strategy
        self.current_index = 0
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5  # seconds
        self.max_errors = 5
        self._health_check_task = None
    
    def add_server(self, server: Server):
        """Add a server to the load balancer."""
        self.servers.append(server)
        logger.info(f"Added server: {server.url}")
    
    def remove_server(self, url: str):
        """Remove a server from the load balancer."""
        self.servers = [s for s in self.servers if s.url != url]
        logger.info(f"Removed server: {url}")
    
    def get_server(self) -> Optional[Server]:
        """Get the next server based on the selected strategy."""
        if not self.servers:
            return None
        
        healthy_servers = [s for s in self.servers if s.is_healthy]
        if not healthy_servers:
            logger.warning("No healthy servers available")
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin(healthy_servers)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections(healthy_servers)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(healthy_servers)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return self._random(healthy_servers)
        elif self.strategy == LoadBalancingStrategy.HEALTH_BASED:
            return self._health_based(healthy_servers)
        else:
            return healthy_servers[0]
    
    def _round_robin(self, servers: List[Server]) -> Server:
        """Round robin selection."""
        server = servers[self.current_index % len(servers)]
        self.current_index += 1
        return server
    
    def _least_connections(self, servers: List[Server]) -> Server:
        """Select server with least connections."""
        return min(servers, key=lambda s: s.current_connections)
    
    def _weighted_round_robin(self, servers: List[Server]) -> Server:
        """Weighted round robin selection."""
        total_weight = sum(s.weight for s in servers)
        if total_weight == 0:
            return servers[0]
        
        # Simple weighted selection
        weights = [s.weight for s in servers]
        selected_index = random.choices(range(len(servers)), weights=weights)[0]
        return servers[selected_index]
    
    def _random(self, servers: List[Server]) -> Server:
        """Random selection."""
        return random.choice(servers)
    
    def _health_based(self, servers: List[Server]) -> Server:
        """Select server based on health metrics."""
        # Score based on response time, error rate, and connections
        scored_servers = []
        for server in servers:
            error_rate = server.error_count / max(server.success_count + server.error_count, 1)
            score = (1 / (server.response_time + 0.1)) * (1 - error_rate) * (1 / (server.current_connections + 1))
            scored_servers.append((server, score))
        
        # Return server with highest score
        return max(scored_servers, key=lambda x: x[1])[0]
    
    async def make_request(self, method: str, path: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make a request through the load balancer."""
        server = self.get_server()
        if not server:
            return None
        
        server.current_connections += 1
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{server.url.rstrip('/')}/{path.lstrip('/')}"
                async with session.request(method, url, **kwargs) as response:
                    result = await response.json()
                    server.success_count += 1
                    return result
        except Exception as e:
            logger.error(f"Request failed to {server.url}: {e}")
            server.error_count += 1
            
            # Mark server as unhealthy if too many errors
            if server.error_count >= self.max_errors:
                server.is_healthy = False
                logger.warning(f"Server {server.url} marked as unhealthy")
            
            return None
        finally:
            server.current_connections -= 1
            server.response_time = time.time() - start_time
    
    async def health_check(self):
        """Perform health check on all servers."""
        for server in self.servers:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{server.url}/health",
                        timeout=aiohttp.ClientTimeout(total=self.health_check_timeout)
                    ) as response:
                        if response.status == 200:
                            server.is_healthy = True
                            server.error_count = 0
                        else:
                            server.is_healthy = False
            except Exception as e:
                logger.warning(f"Health check failed for {server.url}: {e}")
                server.is_healthy = False
            
            server.last_health_check = time.time()
    
    async def start_health_checks(self):
        """Start periodic health checks."""
        while True:
            await self.health_check()
            await asyncio.sleep(self.health_check_interval)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics."""
        healthy_servers = [s for s in self.servers if s.is_healthy]
        total_connections = sum(s.current_connections for s in self.servers)
        total_requests = sum(s.success_count + s.error_count for s in self.servers)
        
        return {
            "strategy": self.strategy.value,
            "total_servers": len(self.servers),
            "healthy_servers": len(healthy_servers),
            "total_connections": total_connections,
            "total_requests": total_requests,
            "servers": [
                {
                    "url": s.url,
                    "is_healthy": s.is_healthy,
                    "current_connections": s.current_connections,
                    "response_time": s.response_time,
                    "success_count": s.success_count,
                    "error_count": s.error_count,
                    "error_rate": s.error_count / max(s.success_count + s.error_count, 1)
                }
                for s in self.servers
            ]
        }

class DatabaseConnectionPool:
    """Database connection pool for optimization."""
    
    def __init__(self, max_connections: int = 20, min_connections: int = 5):
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connections = []
        self.available_connections = asyncio.Queue()
        self.used_connections = set()
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the connection pool."""
        for _ in range(self.min_connections):
            connection = await self._create_connection()
            self.connections.append(connection)
            await self.available_connections.put(connection)
    
    async def _create_connection(self):
        """Create a new database connection."""
        # Mock connection - replace with actual database connection
        return {
            "id": len(self.connections),
            "created_at": time.time(),
            "last_used": time.time()
        }
    
    async def get_connection(self):
        """Get a connection from the pool."""
        async with self._lock:
            if not self.available_connections.empty():
                connection = await self.available_connections.get()
                self.used_connections.add(connection)
                return connection
            
            if len(self.connections) < self.max_connections:
                connection = await self._create_connection()
                self.connections.append(connection)
                self.used_connections.add(connection)
                return connection
            
            # Wait for a connection to become available
            connection = await self.available_connections.get()
            self.used_connections.add(connection)
            return connection
    
    async def return_connection(self, connection):
        """Return a connection to the pool."""
        async with self._lock:
            if connection in self.used_connections:
                self.used_connections.remove(connection)
                connection["last_used"] = time.time()
                await self.available_connections.put(connection)
    
    async def close_all(self):
        """Close all connections."""
        async with self._lock:
            while not self.available_connections.empty():
                await self.available_connections.get()
            
            self.connections.clear()
            self.used_connections.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return {
            "total_connections": len(self.connections),
            "available_connections": self.available_connections.qsize(),
            "used_connections": len(self.used_connections),
            "max_connections": self.max_connections,
            "min_connections": self.min_connections
        }

# Global instances
load_balancer = LoadBalancer(LoadBalancingStrategy.HEALTH_BASED)
db_pool = DatabaseConnectionPool()

# Add some mock servers
load_balancer.add_server(Server("http://localhost:8001", weight=2))
load_balancer.add_server(Server("http://localhost:8002", weight=1))
load_balancer.add_server(Server("http://localhost:8003", weight=3))
