"""
Performance Optimization Module
Sistem performansını optimize eden modül
"""

import asyncio
import time
import psutil
import gc
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performans metrikleri"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    active_connections: int
    response_time_ms: float
    requests_per_second: float
    cache_hit_rate: float
    gc_collections: int

class PerformanceOptimizer:
    """Performans optimizasyon sınıfı"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.optimization_enabled = True
        self.gc_threshold = 80  # Memory %80'e ulaştığında GC çalıştır
        self.cache_cleanup_interval = 300  # 5 dakikada bir cache temizle
        self.last_cleanup = time.time()
        
    async def collect_metrics(self) -> PerformanceMetrics:
        """Sistem metriklerini topla"""
        try:
            # CPU ve Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Network
            network = psutil.net_io_counters()
            
            # Active connections
            try:
                connections = len(psutil.net_connections())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                connections = 0
            
            # Response time (mock)
            response_time = self._calculate_avg_response_time()
            
            # Requests per second (mock)
            rps = self._calculate_requests_per_second()
            
            # Cache hit rate (mock)
            cache_hit_rate = self._calculate_cache_hit_rate()
            
            # GC collections
            gc_stats = gc.get_stats()
            gc_collections = sum(stat['collections'] for stat in gc_stats)
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                memory_available_mb=memory.available / 1024 / 1024,
                disk_usage_percent=(disk.used / disk.total) * 100,
                network_io={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                active_connections=connections,
                response_time_ms=response_time,
                requests_per_second=rps,
                cache_hit_rate=cache_hit_rate,
                gc_collections=gc_collections
            )
            
            self.metrics_history.append(metrics)
            
            # Son 100 metrik tut
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrik toplama hatası: {e}")
            return None
    
    def _calculate_avg_response_time(self) -> float:
        """Ortalama response time hesapla (mock)"""
        if len(self.metrics_history) < 2:
            return 50.0  # Default 50ms
        
        recent_metrics = self.metrics_history[-10:]
        return sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics)
    
    def _calculate_requests_per_second(self) -> float:
        """Saniye başına request sayısı hesapla (mock)"""
        if len(self.metrics_history) < 2:
            return 10.0  # Default 10 RPS
        
        # Son 10 saniyedeki ortalama
        return 15.0 + (psutil.cpu_percent() / 10)  # CPU'ya göre değişken
    
    def _calculate_cache_hit_rate(self) -> float:
        """Cache hit rate hesapla (mock)"""
        return 85.0 + (psutil.virtual_memory().percent / 20)  # Memory'ye göre değişken
    
    async def optimize_memory(self):
        """Memory optimizasyonu"""
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > self.gc_threshold:
                logger.info(f"Memory kullanımı %{memory.percent:.1f} - GC çalıştırılıyor")
                
                # Garbage collection
                collected = gc.collect()
                logger.info(f"GC: {collected} obje temizlendi")
                
                # Cache temizleme
                await self._cleanup_cache()
                
                # Memory kullanımını tekrar kontrol et
                new_memory = psutil.virtual_memory()
                improvement = memory.percent - new_memory.percent
                logger.info(f"Memory optimizasyonu: %{improvement:.1f} iyileştirme")
                
        except Exception as e:
            logger.error(f"Memory optimizasyon hatası: {e}")
    
    async def _cleanup_cache(self):
        """Cache temizleme"""
        try:
            # Mock cache temizleme
            logger.info("Cache temizleme başlatıldı")
            
            # Gerçek implementasyonda burada cache temizleme işlemleri olacak
            await asyncio.sleep(0.1)  # Simüle edilmiş işlem
            
            logger.info("Cache temizleme tamamlandı")
            
        except Exception as e:
            logger.error(f"Cache temizleme hatası: {e}")
    
    async def optimize_cpu(self):
        """CPU optimizasyonu"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > 80:
                logger.info(f"CPU kullanımı %{cpu_percent:.1f} - Optimizasyon başlatılıyor")
                
                # CPU yoğun işlemleri optimize et
                await self._optimize_cpu_intensive_tasks()
                
        except Exception as e:
            logger.error(f"CPU optimizasyon hatası: {e}")
    
    async def _optimize_cpu_intensive_tasks(self):
        """CPU yoğun işlemleri optimize et"""
        try:
            # Mock CPU optimizasyonu
            logger.info("CPU yoğun işlemler optimize ediliyor")
            
            # Gerçek implementasyonda burada CPU optimizasyon işlemleri olacak
            await asyncio.sleep(0.1)
            
            logger.info("CPU optimizasyonu tamamlandı")
            
        except Exception as e:
            logger.error(f"CPU optimizasyon hatası: {e}")
    
    async def auto_optimize(self):
        """Otomatik optimizasyon"""
        try:
            current_time = time.time()
            
            # Periyodik cache temizleme
            if current_time - self.last_cleanup > self.cache_cleanup_interval:
                await self._cleanup_cache()
                self.last_cleanup = current_time
            
            # Memory optimizasyonu
            await self.optimize_memory()
            
            # CPU optimizasyonu
            await self.optimize_cpu()
            
        except Exception as e:
            logger.error(f"Otomatik optimizasyon hatası: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Performans özeti"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        latest = self.metrics_history[-1]
        avg_cpu = sum(m.cpu_percent for m in self.metrics_history[-10:]) / min(10, len(self.metrics_history))
        avg_memory = sum(m.memory_percent for m in self.metrics_history[-10:]) / min(10, len(self.metrics_history))
        avg_response_time = sum(m.response_time_ms for m in self.metrics_history[-10:]) / min(10, len(self.metrics_history))
        
        return {
            "status": "healthy" if latest.memory_percent < 80 and latest.cpu_percent < 80 else "warning",
            "current": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "response_time_ms": latest.response_time_ms,
                "requests_per_second": latest.requests_per_second,
                "cache_hit_rate": latest.cache_hit_rate
            },
            "averages": {
                "cpu_percent": avg_cpu,
                "memory_percent": avg_memory,
                "response_time_ms": avg_response_time
            },
            "optimization_enabled": self.optimization_enabled,
            "last_optimization": self.last_cleanup
        }

# Global instance
performance_optimizer = PerformanceOptimizer()
