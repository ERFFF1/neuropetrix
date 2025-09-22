from celery import Celery
import os

# Celery configuration
celery_app = Celery(
    "neuropetrix",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=[
        "tasks.imaging_tasks",
        "tasks.report_tasks",
        "tasks.audit_tasks"
    ]
)

# Celery settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    task_always_eager=False,  # Set to True for testing
)

# Task routing
celery_app.conf.task_routes = {
    "tasks.imaging_tasks.*": {"queue": "imaging"},
    "tasks.report_tasks.*": {"queue": "reports"},
    "tasks.audit_tasks.*": {"queue": "audit"},
}

if __name__ == "__main__":
    celery_app.start()


