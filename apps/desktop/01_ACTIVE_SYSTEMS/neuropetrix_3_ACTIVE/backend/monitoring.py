from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request
import time
import psutil
import logging

logger = logging.getLogger(__name__)

# Prometheus metrics
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

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of active HTTP requests'
)

PROCESSING_TIME = Histogram(
    'dicom_processing_duration_seconds',
    'DICOM processing duration in seconds',
    ['pipeline_step']
)

REPORT_GENERATION_TIME = Histogram(
    'report_generation_duration_seconds',
    'Report generation duration in seconds',
    ['report_type']
)

SYSTEM_MEMORY = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

SYSTEM_CPU = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

# Middleware for request tracking
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    ACTIVE_REQUESTS.inc()
    
    try:
        response = await call_next(request)
        
        # Record metrics
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
        
    finally:
        ACTIVE_REQUESTS.dec()

# System metrics collection
def collect_system_metrics():
    """Collect system metrics"""
    try:
        # Memory usage
        memory = psutil.virtual_memory()
        SYSTEM_MEMORY.set(memory.used)
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        SYSTEM_CPU.set(cpu_percent)
        
        logger.debug(f"System metrics collected: Memory={memory.percent}%, CPU={cpu_percent}%")
        
    except Exception as e:
        logger.error(f"Error collecting system metrics: {str(e)}")

# Performance monitoring decorator
def monitor_performance(metric_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                PROCESSING_TIME.labels(pipeline_step=metric_name).observe(duration)
        return wrapper
    return decorator

# Health check with metrics
def get_health_status():
    """Get detailed health status with metrics"""
    try:
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "metrics": {
                "memory_usage_percent": memory.percent,
                "cpu_usage_percent": cpu_percent,
                "active_requests": ACTIVE_REQUESTS._value.get(),
                "uptime_seconds": time.time() - psutil.boot_time()
            },
            "thresholds": {
                "memory_warning": 80,
                "memory_critical": 90,
                "cpu_warning": 70,
                "cpu_critical": 85
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

# Metrics endpoint
def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()


