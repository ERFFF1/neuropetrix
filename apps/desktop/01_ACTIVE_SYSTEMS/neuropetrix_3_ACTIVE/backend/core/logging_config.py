import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
import threading
from queue import Queue
import requests
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry["endpoint"] = record.endpoint
        if hasattr(record, 'method'):
            log_entry["method"] = record.method
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        if hasattr(record, 'duration'):
            log_entry["duration"] = record.duration
        if hasattr(record, 'ai_module'):
            log_entry["ai_module"] = record.ai_module
        if hasattr(record, 'workflow_type'):
            log_entry["workflow_type"] = record.workflow_type
        
        return json.dumps(log_entry, ensure_ascii=False)

class ElasticsearchHandler(logging.Handler):
    """Custom handler for sending logs to Elasticsearch."""
    
    def __init__(self, es_host: str = "localhost:9200", index_prefix: str = "neuropetrix"):
        super().__init__()
        self.es_host = es_host
        self.index_prefix = index_prefix
        self.es_client = None
        self.log_queue = Queue()
        self.worker_thread = None
        self.running = False
        
        try:
            self.es_client = Elasticsearch([es_host])
            self.es_client.ping()
            self.running = True
            self.worker_thread = threading.Thread(target=self._process_logs)
            self.worker_thread.daemon = True
            self.worker_thread.start()
            print(f"Elasticsearch handler initialized: {es_host}")
        except ESConnectionError:
            print(f"Failed to connect to Elasticsearch: {es_host}")
            self.es_client = None
    
    def emit(self, record):
        """Emit a log record to Elasticsearch."""
        if not self.es_client or not self.running:
            return
        
        try:
            log_entry = json.loads(self.format(record))
            self.log_queue.put(log_entry)
        except Exception as e:
            print(f"Error formatting log entry: {e}")
    
    def _process_logs(self):
        """Process logs in background thread."""
        while self.running:
            try:
                if not self.log_queue.empty():
                    log_entry = self.log_queue.get(timeout=1)
                    self._send_to_elasticsearch(log_entry)
            except Exception as e:
                print(f"Error processing logs: {e}")
    
    def _send_to_elasticsearch(self, log_entry: Dict[str, Any]):
        """Send log entry to Elasticsearch."""
        try:
            # Create index name with date
            date_str = datetime.now().strftime("%Y.%m.%d")
            index_name = f"{self.index_prefix}-{date_str}"
            
            # Send to Elasticsearch
            self.es_client.index(
                index=index_name,
                body=log_entry,
                doc_type="_doc"
            )
        except Exception as e:
            print(f"Error sending to Elasticsearch: {e}")
    
    def close(self):
        """Close the handler."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
        super().close()

class LogstashHandler(logging.handlers.SocketHandler):
    """Handler for sending logs to Logstash."""
    
    def __init__(self, host: str = "localhost", port: int = 5000):
        super().__init__(host, port)
        self.setFormatter(JSONFormatter())

class KibanaDashboard:
    """Kibana dashboard configuration generator."""
    
    @staticmethod
    def generate_dashboard_config() -> Dict[str, Any]:
        """Generate Kibana dashboard configuration."""
        return {
            "version": "1.0.0",
            "title": "NeuroPETRIX System Dashboard",
            "description": "Comprehensive monitoring dashboard for NeuroPETRIX system",
            "panels": [
                {
                    "title": "API Request Rate",
                    "type": "line_chart",
                    "query": "neuropetrix_api_requests_total",
                    "description": "Rate of API requests over time"
                },
                {
                    "title": "Error Rate",
                    "type": "pie_chart",
                    "query": "level:ERROR",
                    "description": "Distribution of error types"
                },
                {
                    "title": "AI Module Performance",
                    "type": "bar_chart",
                    "query": "ai_module:*",
                    "description": "Performance metrics for AI modules"
                },
                {
                    "title": "System Resources",
                    "type": "gauge",
                    "query": "system_cpu_usage OR system_memory_usage",
                    "description": "System resource utilization"
                },
                {
                    "title": "Clinical Workflows",
                    "type": "table",
                    "query": "workflow_type:*",
                    "description": "Clinical workflow execution statistics"
                }
            ],
            "filters": [
                {
                    "name": "Time Range",
                    "type": "time_range",
                    "default": "last_24h"
                },
                {
                    "name": "Log Level",
                    "type": "terms",
                    "field": "level",
                    "options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                },
                {
                    "name": "AI Module",
                    "type": "terms",
                    "field": "ai_module",
                    "options": ["gemini", "whisper", "monai", "radiomics", "clinical_ai"]
                }
            ]
        }

class LoggingConfig:
    """Centralized logging configuration."""
    
    def __init__(self, 
                 log_level: str = "INFO",
                 enable_elasticsearch: bool = True,
                 enable_logstash: bool = False,
                 enable_file_logging: bool = True,
                 es_host: str = "localhost:9200",
                 logstash_host: str = "localhost",
                 logstash_port: int = 5000):
        
        self.log_level = getattr(logging, log_level.upper())
        self.enable_elasticsearch = enable_elasticsearch
        self.enable_logstash = enable_logstash
        self.enable_file_logging = enable_file_logging
        self.es_host = es_host
        self.logstash_host = logstash_host
        self.logstash_port = logstash_port
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Set log level
        root_logger.setLevel(self.log_level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(console_handler)
        
        # File handler
        if self.enable_file_logging:
            os.makedirs("logs", exist_ok=True)
            
            # Rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                "logs/neuropetrix.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(JSONFormatter())
            root_logger.addHandler(file_handler)
            
            # Error file handler
            error_handler = logging.handlers.RotatingFileHandler(
                "logs/neuropetrix_errors.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(JSONFormatter())
            root_logger.addHandler(error_handler)
        
        # Elasticsearch handler
        if self.enable_elasticsearch:
            try:
                es_handler = ElasticsearchHandler(self.es_host)
                root_logger.addHandler(es_handler)
            except Exception as e:
                print(f"Failed to setup Elasticsearch logging: {e}")
        
        # Logstash handler
        if self.enable_logstash:
            try:
                logstash_handler = LogstashHandler(self.logstash_host, self.logstash_port)
                root_logger.addHandler(logstash_handler)
            except Exception as e:
                print(f"Failed to setup Logstash logging: {e}")
        
        # Configure specific loggers
        self._configure_specific_loggers()
    
    def _configure_specific_loggers(self):
        """Configure specific loggers with appropriate levels."""
        # Reduce noise from external libraries
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("elasticsearch").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        
        # Set application loggers
        logging.getLogger("neuropetrix").setLevel(logging.DEBUG)
        logging.getLogger("neuropetrix.api").setLevel(logging.INFO)
        logging.getLogger("neuropetrix.ai").setLevel(logging.INFO)
        logging.getLogger("neuropetrix.clinical").setLevel(logging.INFO)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the specified name."""
        return logging.getLogger(f"neuropetrix.{name}")

# Global logging configuration
logging_config = LoggingConfig()

# Utility functions for structured logging
def log_api_request(logger: logging.Logger, method: str, endpoint: str, 
                   status_code: int, duration: float, user_id: str = None, 
                   request_id: str = None):
    """Log API request with structured data."""
    extra = {
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "duration": duration
    }
    if user_id:
        extra["user_id"] = user_id
    if request_id:
        extra["request_id"] = request_id
    
    logger.info(f"API Request: {method} {endpoint}", extra=extra)

def log_ai_operation(logger: logging.Logger, ai_module: str, task_type: str, 
                    status: str, duration: float, user_id: str = None):
    """Log AI operation with structured data."""
    extra = {
        "ai_module": ai_module,
        "task_type": task_type,
        "status": status,
        "duration": duration
    }
    if user_id:
        extra["user_id"] = user_id
    
    logger.info(f"AI Operation: {ai_module} - {task_type}", extra=extra)

def log_clinical_workflow(logger: logging.Logger, workflow_type: str, 
                         status: str, duration: float, user_id: str = None):
    """Log clinical workflow with structured data."""
    extra = {
        "workflow_type": workflow_type,
        "status": status,
        "duration": duration
    }
    if user_id:
        extra["user_id"] = user_id
    
    logger.info(f"Clinical Workflow: {workflow_type}", extra=extra)

def log_security_event(logger: logging.Logger, event_type: str, 
                      user_id: str = None, ip_address: str = None, 
                      details: str = None):
    """Log security event with structured data."""
    extra = {
        "event_type": event_type
    }
    if user_id:
        extra["user_id"] = user_id
    if ip_address:
        extra["ip_address"] = ip_address
    if details:
        extra["details"] = details
    
    logger.warning(f"Security Event: {event_type}", extra=extra)
