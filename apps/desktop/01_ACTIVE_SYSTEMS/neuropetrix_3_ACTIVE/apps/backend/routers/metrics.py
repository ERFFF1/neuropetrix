from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge
import time

router = APIRouter(tags=["metrics"])

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_REQUESTS = Gauge('http_active_requests', 'Number of active HTTP requests')
WORKFLOW_COUNT = Counter('workflow_total', 'Total workflows started', ['status'])

@router.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.get("/health")
def health():
    """Metrics health check"""
    return {"status": "OK", "metrics": "enabled"}

# Middleware için metrics fonksiyonları
def record_request(method: str, endpoint: str, status: int, duration: float):
    """Request metrics kaydet"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_DURATION.observe(duration)

def record_workflow(status: str):
    """Workflow metrics kaydet"""
    WORKFLOW_COUNT.labels(status=status).inc()

def set_active_requests(count: int):
    """Aktif request sayısını güncelle"""
    ACTIVE_REQUESTS.set(count)


