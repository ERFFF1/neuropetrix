from fastapi import APIRouter
from datetime import datetime
import psutil
import os

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    """Sistem sağlık kontrolü"""
    try:
        # Sistem bilgileri
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "uptime": psutil.boot_time()
            },
            "services": {
                "database": "online",
                "api": "online",
                "ai_services": "online"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/version")
async def get_version():
    """API versiyonu"""
    return {
        "version": "1.0.0",
        "build_date": "2024-01-15",
        "features": [
            "PICO Automation",
            "Multimodal Fusion", 
            "Clinical Feedback",
            "Compliance Panel"
        ]
    }
