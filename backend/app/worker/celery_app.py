import sys
import asyncio
from celery import Celery
from app.core.config import get_settings

# Fix for Windows Celery async loop issue: AttributeError 'NoneType' object has no attribute 'send'
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

settings = get_settings()

celery_app = Celery(
    "pdf_processing",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks", "app.worker.cleanup"]
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task safety and visibility
    task_acks_late=True, # Task is acknowledged only after it's finished
    task_reject_on_worker_lost=True, # If worker crashes, task is put back on queue
    worker_prefetch_multiplier=1, # One task at a time per worker for resource heavy PDF jobs
    
    # Timeouts (global defaults)
    task_time_limit=600, # 10 minutes hard limit
    task_soft_time_limit=300, # 5 minutes soft limit
    
    # Queue separation (prep for future)
    # Removed for now to ensure default worker picks up tasks
    # task_routes={
    #     "app.worker.tasks.*": {"queue": "ingestion"},
    #     "app.worker.cleanup.*": {"queue": "cleanup"},
    # }
)

if __name__ == "__main__":
    celery_app.start()
