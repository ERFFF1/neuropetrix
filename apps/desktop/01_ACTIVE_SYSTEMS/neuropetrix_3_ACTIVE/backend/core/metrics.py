from prometheus_client import Counter, Histogram, Gauge, Summary, Info, CollectorRegistry, generate_latest
import time
import psutil
import threading
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Create custom registry
registry = CollectorRegistry()

# API Metrics
api_requests_total = Counter(
    'neuropetrix_api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

api_request_duration = Histogram(
    'neuropetrix_api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    registry=registry
)

api_request_size = Histogram(
    'neuropetrix_api_request_size_bytes',
    'API request size in bytes',
    ['method', 'endpoint'],
    registry=registry
)

# AI Metrics
ai_requests_total = Counter(
    'neuropetrix_ai_requests_total',
    'Total number of AI requests',
    ['ai_module', 'task_type', 'status'],
    registry=registry
)

ai_processing_time = Histogram(
    'neuropetrix_ai_processing_time_seconds',
    'AI processing time in seconds',
    ['ai_module', 'task_type'],
    registry=registry
)

ai_accuracy = Gauge(
    'neuropetrix_ai_accuracy',
    'AI model accuracy',
    ['ai_module', 'model_version'],
    registry=registry
)

# Clinical Workflow Metrics
clinical_workflows_total = Counter(
    'neuropetrix_clinical_workflows_total',
    'Total number of clinical workflows',
    ['workflow_type', 'status'],
    registry=registry
)

workflow_duration = Histogram(
    'neuropetrix_workflow_duration_seconds',
    'Clinical workflow duration in seconds',
    ['workflow_type'],
    registry=registry
)

# System Metrics
system_cpu_usage = Gauge(
    'neuropetrix_system_cpu_usage_percent',
    'System CPU usage percentage',
    registry=registry
)

system_memory_usage = Gauge(
    'neuropetrix_system_memory_usage_percent',
    'System memory usage percentage',
    registry=registry
)

system_disk_usage = Gauge(
    'neuropetrix_system_disk_usage_percent',
    'System disk usage percentage',
    registry=registry
)

active_connections = Gauge(
    'neuropetrix_active_connections',
    'Number of active connections',
    registry=registry
)

# Cache Metrics
cache_hits_total = Counter(
    'neuropetrix_cache_hits_total',
    'Total number of cache hits',
    ['cache_type'],
    registry=registry
)

cache_misses_total = Counter(
    'neuropetrix_cache_misses_total',
    'Total number of cache misses',
    ['cache_type'],
    registry=registry
)

cache_size = Gauge(
    'neuropetrix_cache_size',
    'Cache size in bytes',
    ['cache_type'],
    registry=registry
)

# Database Metrics
db_connections_active = Gauge(
    'neuropetrix_db_connections_active',
    'Number of active database connections',
    registry=registry
)

db_query_duration = Histogram(
    'neuropetrix_db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    registry=registry
)

db_queries_total = Counter(
    'neuropetrix_db_queries_total',
    'Total number of database queries',
    ['query_type', 'status'],
    registry=registry
)

# Security Metrics
auth_attempts_total = Counter(
    'neuropetrix_auth_attempts_total',
    'Total number of authentication attempts',
    ['result'],
    registry=registry
)

failed_logins_total = Counter(
    'neuropetrix_failed_logins_total',
    'Total number of failed login attempts',
    ['username'],
    registry=registry
)

# Business Metrics
patients_processed_total = Counter(
    'neuropetrix_patients_processed_total',
    'Total number of patients processed',
    ['processing_type'],
    registry=registry
)

reports_generated_total = Counter(
    'neuropetrix_reports_generated_total',
    'Total number of reports generated',
    ['report_type'],
    registry=registry
)

# Application Info
app_info = Info(
    'neuropetrix_app_info',
    'Application information',
    registry=registry
)

class MetricsCollector:
    """Centralized metrics collection and management."""
    
    def __init__(self):
        self.start_time = time.time()
        self._system_metrics_thread = None
        self._running = False
        
        # Set application info
        app_info.info({
            'version': '1.5.0',
            'build': 'production',
            'environment': 'development'
        })
    
    def start_system_metrics_collection(self):
        """Start collecting system metrics in background."""
        if self._running:
            return
        
        self._running = True
        self._system_metrics_thread = threading.Thread(target=self._collect_system_metrics)
        self._system_metrics_thread.daemon = True
        self._system_metrics_thread.start()
        logger.info("System metrics collection started")
    
    def stop_system_metrics_collection(self):
        """Stop collecting system metrics."""
        self._running = False
        if self._system_metrics_thread:
            self._system_metrics_thread.join()
        logger.info("System metrics collection stopped")
    
    def _collect_system_metrics(self):
        """Collect system metrics periodically."""
        while self._running:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                system_cpu_usage.set(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                system_memory_usage.set(memory.percent)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                system_disk_usage.set(disk_percent)
                
                # Network connections
                connections = len(psutil.net_connections())
                active_connections.set(connections)
                
                time.sleep(10)  # Collect every 10 seconds
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                time.sleep(10)
    
    def record_api_request(self, method: str, endpoint: str, status_code: int, duration: float, size: int = 0):
        """Record API request metrics."""
        api_requests_total.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()
        api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        if size > 0:
            api_request_size.labels(method=method, endpoint=endpoint).observe(size)
    
    def record_ai_request(self, ai_module: str, task_type: str, status: str, duration: float):
        """Record AI request metrics."""
        ai_requests_total.labels(ai_module=ai_module, task_type=task_type, status=status).inc()
        ai_processing_time.labels(ai_module=ai_module, task_type=task_type).observe(duration)
    
    def record_clinical_workflow(self, workflow_type: str, status: str, duration: float):
        """Record clinical workflow metrics."""
        clinical_workflows_total.labels(workflow_type=workflow_type, status=status).inc()
        workflow_duration.labels(workflow_type=workflow_type).observe(duration)
    
    def record_cache_operation(self, cache_type: str, hit: bool):
        """Record cache operation metrics."""
        if hit:
            cache_hits_total.labels(cache_type=cache_type).inc()
        else:
            cache_misses_total.labels(cache_type=cache_type).inc()
    
    def record_database_operation(self, query_type: str, status: str, duration: float):
        """Record database operation metrics."""
        db_queries_total.labels(query_type=query_type, status=status).inc()
        db_query_duration.labels(query_type=query_type).observe(duration)
    
    def record_auth_attempt(self, result: str, username: str = None):
        """Record authentication attempt metrics."""
        auth_attempts_total.labels(result=result).inc()
        if result == "failed" and username:
            failed_logins_total.labels(username=username).inc()
    
    def record_business_metric(self, metric_type: str, subtype: str = None):
        """Record business metrics."""
        if metric_type == "patient_processed":
            patients_processed_total.labels(processing_type=subtype or "default").inc()
        elif metric_type == "report_generated":
            reports_generated_total.labels(report_type=subtype or "default").inc()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "uptime_human": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
            "system_metrics_collection": self._running,
            "registry_size": len(list(registry.collect())),
            "metrics_available": [
                "api_requests_total",
                "api_request_duration",
                "ai_requests_total",
                "ai_processing_time",
                "clinical_workflows_total",
                "workflow_duration",
                "system_cpu_usage",
                "system_memory_usage",
                "system_disk_usage",
                "active_connections",
                "cache_hits_total",
                "cache_misses_total",
                "db_connections_active",
                "db_query_duration",
                "auth_attempts_total",
                "patients_processed_total",
                "reports_generated_total"
            ]
        }
    
    def export_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        return generate_latest(registry).decode('utf-8')

# Global metrics collector
metrics_collector = MetricsCollector()

# Decorator for automatic metrics collection
def track_metrics(metric_type: str, labels: Dict[str, str] = None):
    """Decorator to automatically track metrics for functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                
                if metric_type == "api_request":
                    method = labels.get("method", "unknown")
                    endpoint = labels.get("endpoint", "unknown")
                    status_code = labels.get("status_code", "200")
                    metrics_collector.record_api_request(method, endpoint, int(status_code), duration)
                
                elif metric_type == "ai_request":
                    ai_module = labels.get("ai_module", "unknown")
                    task_type = labels.get("task_type", "unknown")
                    metrics_collector.record_ai_request(ai_module, task_type, status, duration)
                
                elif metric_type == "clinical_workflow":
                    workflow_type = labels.get("workflow_type", "unknown")
                    metrics_collector.record_clinical_workflow(workflow_type, status, duration)
                
                elif metric_type == "database_query":
                    query_type = labels.get("query_type", "unknown")
                    metrics_collector.record_database_operation(query_type, status, duration)
        
        return wrapper
    return decorator
