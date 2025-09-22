from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
import psutil
import time
import asyncio
from datetime import datetime, timedelta

router = APIRouter(prefix="/monitoring", tags=["System Monitoring"])

class SystemMetrics(BaseModel):
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    active_connections: int
    uptime_seconds: float

class PerformanceMetrics(BaseModel):
    api_response_times: Dict[str, float]
    request_counts: Dict[str, int]
    error_rates: Dict[str, float]
    throughput_per_second: float

class HealthStatus(BaseModel):
    status: str
    services: Dict[str, str]
    last_check: str
    uptime: str

# Mock data for demonstration
_start_time = time.time()
_request_counts = {}
_response_times = {}

@router.get("/system-metrics", response_model=SystemMetrics)
async def get_system_metrics():
    """Sistem kaynak kullanım metriklerini döndürür."""
    try:
        # CPU kullanımı
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory kullanımı
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk kullanımı
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Network I/O
        network = psutil.net_io_counters()
        network_io = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }
        
        # Active connections
        try:
            connections = len(psutil.net_connections())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            connections = 0
        
        # Uptime
        uptime_seconds = time.time() - _start_time
        
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            network_io=network_io,
            active_connections=connections,
            uptime_seconds=uptime_seconds
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sistem metrikleri alınamadı: {str(e)}")

@router.get("/performance-metrics", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """API performans metriklerini döndürür."""
    try:
        # Mock performance data
        api_response_times = {
            "/health": 45.2,
            "/ai-manager/status": 120.5,
            "/clinical-workflow/analyze-icd": 89.3,
            "/io-flows/definitions": 67.8
        }
        
        request_counts = {
            "/health": 1250,
            "/ai-manager/status": 890,
            "/clinical-workflow/analyze-icd": 456,
            "/io-flows/definitions": 234
        }
        
        error_rates = {
            "/health": 0.1,
            "/ai-manager/status": 0.5,
            "/clinical-workflow/analyze-icd": 1.2,
            "/io-flows/definitions": 0.8
        }
        
        throughput_per_second = 15.7
        
        return PerformanceMetrics(
            api_response_times=api_response_times,
            request_counts=request_counts,
            error_rates=error_rates,
            throughput_per_second=throughput_per_second
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performans metrikleri alınamadı: {str(e)}")

@router.get("/health-status", response_model=HealthStatus)
async def get_health_status():
    """Sistem sağlık durumunu döndürür."""
    try:
        services = {
            "backend": "healthy",
            "database": "healthy",
            "ai_manager": "healthy",
            "clinical_workflow": "healthy",
            "io_flows": "healthy"
        }
        
        uptime = str(timedelta(seconds=int(time.time() - _start_time)))
        
        return HealthStatus(
            status="healthy",
            services=services,
            last_check=datetime.now().isoformat(),
            uptime=uptime
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sağlık durumu alınamadı: {str(e)}")

@router.get("/alerts")
async def get_system_alerts():
    """Sistem uyarılarını döndürür."""
    try:
        alerts = []
        
        # CPU uyarısı
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            alerts.append({
                "type": "warning",
                "message": f"Yüksek CPU kullanımı: {cpu_percent}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # Memory uyarısı
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            alerts.append({
                "type": "critical",
                "message": f"Yüksek bellek kullanımı: {memory.percent}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # Disk uyarısı
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > 90:
            alerts.append({
                "type": "critical",
                "message": f"Yüksek disk kullanımı: {disk_percent:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
        
        return {"alerts": alerts, "total_alerts": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Uyarılar alınamadı: {str(e)}")

@router.post("/test-performance")
async def test_performance():
    """Sistem performansını test eder."""
    try:
        start_time = time.time()
        
        # CPU test
        cpu_start = psutil.cpu_percent()
        await asyncio.sleep(0.1)
        cpu_end = psutil.cpu_percent()
        
        # Memory test
        memory = psutil.virtual_memory()
        
        # Response time
        response_time = (time.time() - start_time) * 1000
        
        return {
            "test_completed": True,
            "response_time_ms": round(response_time, 2),
            "cpu_usage": cpu_end,
            "memory_usage": memory.percent,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performans testi başarısız: {str(e)}")
