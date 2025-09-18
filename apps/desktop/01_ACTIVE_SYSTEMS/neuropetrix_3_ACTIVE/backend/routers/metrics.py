from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Dict, Any
from backend.core.metrics import metrics_collector
from backend.routers.auth import get_current_user, require_permissions
from backend.core.auth import User

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("/prometheus", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    """Get metrics in Prometheus format."""
    try:
        return metrics_collector.export_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export metrics: {str(e)}")

@router.get("/summary")
async def get_metrics_summary(admin_user: User = Depends(require_permissions(["admin"]))):
    """Get metrics summary (admin only)."""
    try:
        return metrics_collector.get_metrics_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics summary: {str(e)}")

@router.post("/start-collection")
async def start_metrics_collection(admin_user: User = Depends(require_permissions(["admin"]))):
    """Start system metrics collection (admin only)."""
    try:
        metrics_collector.start_system_metrics_collection()
        return {"message": "System metrics collection started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start metrics collection: {str(e)}")

@router.post("/stop-collection")
async def stop_metrics_collection(admin_user: User = Depends(require_permissions(["admin"]))):
    """Stop system metrics collection (admin only)."""
    try:
        metrics_collector.stop_system_metrics_collection()
        return {"message": "System metrics collection stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop metrics collection: {str(e)}")

@router.get("/health")
async def get_metrics_health():
    """Get metrics system health."""
    try:
        summary = metrics_collector.get_metrics_summary()
        return {
            "status": "healthy",
            "uptime": summary["uptime_human"],
            "system_metrics_collection": summary["system_metrics_collection"],
            "available_metrics": len(summary["metrics_available"])
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
