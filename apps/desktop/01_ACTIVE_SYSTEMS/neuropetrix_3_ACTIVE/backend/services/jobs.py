import uuid
import threading
import time
from typing import Dict, Any, Callable
from datetime import datetime

_jobs: Dict[str, dict] = {}

def enqueue(fn: Callable, *args, **kwargs) -> str:
    """Fonksiyonu arka planda çalıştır ve job_id döndür"""
    jid = uuid.uuid4().hex[:8]
    _jobs[jid] = {
        "status": "queued",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "function": fn.__name__
    }
    
    def run():
        _jobs[jid]["status"] = "running"
        _jobs[jid]["started_at"] = datetime.utcnow().isoformat() + "Z"
        try:
            res = fn(*args, **kwargs)
            _jobs[jid].update({
                "status": "done",
                "result": res,
                "completed_at": datetime.utcnow().isoformat() + "Z"
            })
        except Exception as e:
            _jobs[jid].update({
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat() + "Z"
            })
    
    threading.Thread(target=run, daemon=True).start()
    return jid

def get(jid: str) -> dict:
    """Job durumunu getir"""
    return _jobs.get(jid, {"status": "unknown"})

def list_jobs() -> Dict[str, dict]:
    """Tüm job'ları listele"""
    return _jobs

def clear_completed_jobs():
    """Tamamlanan job'ları temizle"""
    global _jobs
    _jobs = {jid: job for jid, job in _jobs.items() if job["status"] in ["queued", "running"]}

def get_job_stats() -> dict:
    """Job istatistiklerini getir"""
    stats = {"total": len(_jobs)}
    for status in ["queued", "running", "done", "failed"]:
        stats[status] = len([j for j in _jobs.values() if j["status"] == status])
    return stats


