"""
Metrics Router
NeuroPETRIX - Prometheus metrics API'leri
"""

import logging
from fastapi import APIRouter, Request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["Metrics"])

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CASES = Gauge(
    'neuropetrix_cases_active',
    'Number of active cases'
)

AI_QUEUE_SIZE = Gauge(
    'neuropetrix_ai_queue_size',
    'Number of AI analysis jobs in queue'
)

AI_ANALYSIS_DURATION = Histogram(
    'neuropetrix_ai_analysis_duration_seconds',
    'AI analysis duration in seconds',
    ['analysis_type']
)

AI_ANALYSIS_SUCCESS = Counter(
    'neuropetrix_ai_analysis_total',
    'Total AI analyses',
    ['analysis_type', 'status']
)

NOTIFICATION_COUNT = Counter(
    'neuropetrix_notifications_total',
    'Total notifications sent',
    ['type', 'priority']
)

WEBSOCKET_CONNECTIONS = Gauge(
    'neuropetrix_websocket_connections',
    'Number of active WebSocket connections'
)

DATABASE_CONNECTIONS = Gauge(
    'neuropetrix_database_connections',
    'Number of active database connections'
)

@router.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """HTTP istekleri için metrics toplama middleware"""
    start_time = time.time()
    
    # İsteği işle
    response = await call_next(request)
    
    # Metrics topla
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

@router.get("/")
async def get_metrics():
    """Prometheus metrics endpoint"""
    try:
        # Güncel metrikleri güncelle
        await update_metrics()
        
        # Metrics'i döndür
        metrics_data = generate_latest()
        return Response(
            content=metrics_data,
            media_type=CONTENT_TYPE_LATEST
        )
        
    except Exception as e:
        logger.error(f"Metrics alınamadı: {e}")
        return Response(
            content="Error generating metrics",
            status_code=500
        )

async def update_metrics():
    """Güncel metrikleri güncelle"""
    try:
        # Aktif vaka sayısını güncelle
        # TODO: Gerçek veritabanından al
        ACTIVE_CASES.set(5)
        
        # AI kuyruk boyutunu güncelle
        # TODO: Gerçek kuyruk boyutundan al
        AI_QUEUE_SIZE.set(2)
        
        # WebSocket bağlantı sayısını güncelle
        # TODO: Gerçek WebSocket manager'dan al
        WEBSOCKET_CONNECTIONS.set(3)
        
        # Veritabanı bağlantı sayısını güncelle
        # TODO: Gerçek veritabanı bağlantı sayısından al
        DATABASE_CONNECTIONS.set(1)
        
    except Exception as e:
        logger.error(f"Metrics güncellenemedi: {e}")

@router.get("/health")
async def health_check():
    """Metrics servis sağlık kontrolü"""
    return {
        "status": "healthy",
        "service": "metrics",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "metrics_available": [
            "http_requests_total",
            "http_request_duration_seconds",
            "neuropetrix_cases_active",
            "neuropetrix_ai_queue_size",
            "neuropetrix_ai_analysis_duration_seconds",
            "neuropetrix_ai_analysis_total",
            "neuropetrix_notifications_total",
            "neuropetrix_websocket_connections",
            "neuropetrix_database_connections"
        ]
    }

# Metrics helper functions
def record_ai_analysis(analysis_type: str, duration: float, success: bool):
    """AI analizi metrics'ini kaydet"""
    try:
        AI_ANALYSIS_DURATION.labels(analysis_type=analysis_type).observe(duration)
        AI_ANALYSIS_SUCCESS.labels(
            analysis_type=analysis_type,
            status="success" if success else "failure"
        ).inc()
    except Exception as e:
        logger.error(f"AI analysis metrics kaydedilemedi: {e}")

def record_notification(notification_type: str, priority: str):
    """Bildirim metrics'ini kaydet"""
    try:
        NOTIFICATION_COUNT.labels(
            type=notification_type,
            priority=priority
        ).inc()
    except Exception as e:
        logger.error(f"Notification metrics kaydedilemedi: {e}")
