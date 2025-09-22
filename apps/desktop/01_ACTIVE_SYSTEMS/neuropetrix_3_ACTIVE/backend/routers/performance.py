"""
Performance Optimization Router
Performans optimizasyonu için API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from backend.core.performance import performance_optimizer, PerformanceMetrics
import asyncio

router = APIRouter(prefix="/performance", tags=["Performance"])

@router.get("/metrics")
async def get_performance_metrics() -> PerformanceMetrics:
    """Güncel performans metriklerini döndürür"""
    try:
        metrics = await performance_optimizer.collect_metrics()
        if metrics is None:
            raise HTTPException(status_code=500, detail="Metrik toplama başarısız")
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performans metrikleri alınamadı: {e}")

@router.get("/summary")
async def get_performance_summary() -> Dict[str, Any]:
    """Performans özetini döndürür"""
    try:
        return performance_optimizer.get_performance_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performans özeti alınamadı: {e}")

@router.post("/optimize/memory")
async def optimize_memory(background_tasks: BackgroundTasks):
    """Memory optimizasyonu başlatır"""
    try:
        background_tasks.add_task(performance_optimizer.optimize_memory)
        return {"message": "Memory optimizasyonu başlatıldı", "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory optimizasyonu başlatılamadı: {e}")

@router.post("/optimize/cpu")
async def optimize_cpu(background_tasks: BackgroundTasks):
    """CPU optimizasyonu başlatır"""
    try:
        background_tasks.add_task(performance_optimizer.optimize_cpu)
        return {"message": "CPU optimizasyonu başlatıldı", "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CPU optimizasyonu başlatılamadı: {e}")

@router.post("/optimize/auto")
async def auto_optimize(background_tasks: BackgroundTasks):
    """Otomatik optimizasyon başlatır"""
    try:
        background_tasks.add_task(performance_optimizer.auto_optimize)
        return {"message": "Otomatik optimizasyon başlatıldı", "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Otomatik optimizasyon başlatılamadı: {e}")

@router.get("/health")
async def performance_health():
    """Performans servisinin sağlık durumu"""
    try:
        summary = performance_optimizer.get_performance_summary()
        return {
            "status": "healthy",
            "message": "Performance optimization service is running",
            "optimization_enabled": summary.get("optimization_enabled", True)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Performance service error: {e}",
            "optimization_enabled": False
        }
