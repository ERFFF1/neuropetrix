"""
Performance Monitoring Middleware
Sistem performansını izler ve optimize eder
"""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any
import psutil
import os

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.total_response_time = 0
        self.slow_requests = []
        
    async def dispatch(self, request: Request, call_next):
        # Request başlangıcı
        start_time = time.time()
        self.request_count += 1
        
        # Memory kullanımı
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Request işle
        response = await call_next(request)
        
        # Response süresi
        response_time = time.time() - start_time
        self.total_response_time += response_time
        
        # Memory kullanımı
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_diff = memory_after - memory_before
        
        # Yavaş request'leri kaydet
        if response_time > 1.0:  # 1 saniyeden yavaş
            self.slow_requests.append({
                "path": str(request.url.path),
                "method": request.method,
                "response_time": response_time,
                "memory_diff": memory_diff
            })
        
        # Performance log
        logger.info(
            f"Request: {request.method} {request.url.path} | "
            f"Time: {response_time:.3f}s | "
            f"Memory: {memory_diff:+.1f}MB | "
            f"Total: {self.request_count}"
        )
        
        # Response header'a performance bilgisi ekle
        response.headers["X-Response-Time"] = f"{response_time:.3f}s"
        response.headers["X-Memory-Diff"] = f"{memory_diff:+.1f}MB"
        
        return response
    
    def get_stats(self) -> Dict[str, Any]:
        """Performance istatistiklerini döndür"""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        return {
            "total_requests": self.request_count,
            "average_response_time": f"{avg_response_time:.3f}s",
            "slow_requests_count": len(self.slow_requests),
            "slow_requests": self.slow_requests[-10:],  # Son 10 yavaş request
            "memory_usage_mb": psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024,
            "cpu_percent": psutil.Process(os.getpid()).cpu_percent()
        }

# Performance decorator
def monitor_performance(func):
    """Fonksiyon performansını izler"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            
            execution_time = end_time - start_time
            memory_diff = end_memory - start_memory
            
            logger.info(
                f"Function: {func.__name__} | "
                f"Time: {execution_time:.3f}s | "
                f"Memory: {memory_diff:+.1f}MB"
            )
    
    return wrapper


