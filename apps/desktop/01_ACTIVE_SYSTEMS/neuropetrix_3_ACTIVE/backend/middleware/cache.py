"""
Cache Middleware
Response'ları cache'ler ve performansı artırır
"""
import time
import hashlib
import json
from typing import Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class CacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, cache_ttl: int = 300):  # 5 dakika default
        super().__init__(app)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = cache_ttl
        
    def _generate_cache_key(self, request: Request) -> str:
        """Request için cache key oluştur"""
        # URL + method + query params + body hash
        key_parts = [
            request.url.path,
            request.method,
            str(sorted(request.query_params.items())),
        ]
        
        # Body varsa hash'le
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = request.body()
                if body:
                    body_hash = hashlib.md5(body).hexdigest()
                    key_parts.append(body_hash)
            except:
                pass
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_cacheable(self, request: Request, response: Response) -> bool:
        """Response cache'lenebilir mi?"""
        # Sadece GET request'leri cache'le
        if request.method != "GET":
            return False
        
        # Status code 200 olmalı
        if response.status_code != 200:
            return False
        
        # Cache-Control header kontrol et
        cache_control = response.headers.get("Cache-Control", "")
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False
        
        return True
    
    async def dispatch(self, request: Request, call_next):
        # Cache key oluştur
        cache_key = self._generate_cache_key(request)
        
        # Cache'den kontrol et
        if request.method == "GET" and cache_key in self.cache:
            cached_item = self.cache[cache_key]
            
            # TTL kontrol et
            if time.time() - cached_item["timestamp"] < self.cache_ttl:
                logger.info(f"Cache HIT: {request.url.path}")
                
                # Cached response'u döndür
                response = Response(
                    content=cached_item["content"],
                    status_code=cached_item["status_code"],
                    headers=cached_item["headers"]
                )
                response.headers["X-Cache"] = "HIT"
                return response
        
        # Normal request işle
        response = await call_next(request)
        
        # Cache'lenebilir mi?
        if self._is_cacheable(request, response):
            try:
                # Response content'ini al
                content = b""
                async for chunk in response.body_iterator:
                    content += chunk
                
                # Cache'e kaydet
                self.cache[cache_key] = {
                    "content": content,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "timestamp": time.time()
                }
                
                # Response'u yeniden oluştur
                response = Response(
                    content=content,
                    status_code=response.status_code,
                    headers=response.headers
                )
                response.headers["X-Cache"] = "MISS"
                
                logger.info(f"Cache MISS: {request.url.path}")
                
            except Exception as e:
                logger.warning(f"Cache error: {e}")
        
        return response
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Cache istatistiklerini döndür"""
        current_time = time.time()
        expired_keys = []
        
        # Expired cache'leri temizle
        for key, item in self.cache.items():
            if current_time - item["timestamp"] > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        return {
            "total_cached_items": len(self.cache),
            "cache_ttl_seconds": self.cache_ttl,
            "expired_items_cleaned": len(expired_keys),
            "cache_size_mb": sum(
                len(str(item)) for item in self.cache.values()
            ) / 1024 / 1024
        }
    
    def clear_cache(self):
        """Tüm cache'i temizle"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def invalidate_path(self, path: str):
        """Belirli path'deki cache'leri temizle"""
        keys_to_remove = []
        for key, item in self.cache.items():
            if path in str(item.get("content", "")):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
        
        logger.info(f"Cache invalidated for path: {path} ({len(keys_to_remove)} items)")


