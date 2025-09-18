import redis
import json
import pickle
from typing import Any, Optional, Union, Dict
from datetime import datetime, timedelta
import asyncio
import hashlib
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Advanced caching system with Redis and in-memory fallback."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", fallback_to_memory: bool = True):
        self.redis_client = None
        self.memory_cache = {}
        self.fallback_to_memory = fallback_to_memory
        
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()  # Test connection
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using memory cache fallback.")
            self.redis_client = None
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for storage."""
        if isinstance(value, (str, int, float, bool)):
            return json.dumps(value)
        else:
            return pickle.dumps(value).hex()
    
    def _deserialize_value(self, value: str, is_pickle: bool = False) -> Any:
        """Deserialize value from storage."""
        try:
            if is_pickle:
                return pickle.loads(bytes.fromhex(value))
            else:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cache value with TTL."""
        try:
            serialized_value = self._serialize_value(value)
            
            if self.redis_client:
                return self.redis_client.setex(key, ttl, serialized_value)
            elif self.fallback_to_memory:
                expire_time = datetime.now() + timedelta(seconds=ttl)
                self.memory_cache[key] = {
                    'value': serialized_value,
                    'expires': expire_time
                }
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
        
        return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value."""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return self._deserialize_value(value)
            elif self.fallback_to_memory and key in self.memory_cache:
                cache_entry = self.memory_cache[key]
                if datetime.now() < cache_entry['expires']:
                    return self._deserialize_value(cache_entry['value'])
                else:
                    del self.memory_cache[key]
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    def delete(self, key: str) -> bool:
        """Delete cache value."""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            elif self.fallback_to_memory and key in self.memory_cache:
                del self.memory_cache[key]
                return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
        
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if self.redis_client:
                return bool(self.redis_client.exists(key))
            elif self.fallback_to_memory:
                if key in self.memory_cache:
                    cache_entry = self.memory_cache[key]
                    if datetime.now() < cache_entry['expires']:
                        return True
                    else:
                        del self.memory_cache[key]
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
        
        return False
    
    def clear(self) -> bool:
        """Clear all cache."""
        try:
            if self.redis_client:
                return self.redis_client.flushdb()
            elif self.fallback_to_memory:
                self.memory_cache.clear()
                return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "redis_connected": self.redis_client is not None,
            "memory_cache_size": len(self.memory_cache),
            "fallback_enabled": self.fallback_to_memory
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats.update({
                    "redis_used_memory": info.get("used_memory_human"),
                    "redis_connected_clients": info.get("connected_clients"),
                    "redis_keyspace_hits": info.get("keyspace_hits"),
                    "redis_keyspace_misses": info.get("keyspace_misses")
                })
            except Exception as e:
                logger.error(f"Redis stats error: {e}")
        
        return stats

# Global cache instance
cache_manager = CacheManager()

def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

class CacheInvalidation:
    """Cache invalidation strategies."""
    
    @staticmethod
    def invalidate_pattern(pattern: str):
        """Invalidate all keys matching pattern."""
        if cache_manager.redis_client:
            try:
                keys = cache_manager.redis_client.keys(pattern)
                if keys:
                    cache_manager.redis_client.delete(*keys)
                    logger.info(f"Invalidated {len(keys)} keys matching pattern: {pattern}")
            except Exception as e:
                logger.error(f"Pattern invalidation error: {e}")
        else:
            # Memory cache pattern invalidation
            keys_to_delete = [key for key in cache_manager.memory_cache.keys() if pattern.replace('*', '') in key]
            for key in keys_to_delete:
                del cache_manager.memory_cache[key]
            logger.info(f"Invalidated {len(keys_to_delete)} memory cache keys matching pattern: {pattern}")
    
    @staticmethod
    def invalidate_user_data(user_id: str):
        """Invalidate all cache entries for a specific user."""
        CacheInvalidation.invalidate_pattern(f"user:{user_id}:*")
    
    @staticmethod
    def invalidate_patient_data(patient_id: str):
        """Invalidate all cache entries for a specific patient."""
        CacheInvalidation.invalidate_pattern(f"patient:{patient_id}:*")
    
    @staticmethod
    def invalidate_ai_results():
        """Invalidate all AI-related cache entries."""
        CacheInvalidation.invalidate_pattern("ai:*")

class CacheMetrics:
    """Cache performance metrics."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
    
    def record_hit(self):
        self.hits += 1
    
    def record_miss(self):
        self.misses += 1
    
    def record_set(self):
        self.sets += 1
    
    def record_delete(self):
        self.deletes += 1
    
    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "hit_rate": self.get_hit_rate()
        }

# Global metrics instance
cache_metrics = CacheMetrics()
