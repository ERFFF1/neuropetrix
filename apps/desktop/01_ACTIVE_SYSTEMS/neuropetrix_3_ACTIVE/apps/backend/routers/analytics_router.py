from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import sqlite3
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard"])

class AnalyticsRequest(BaseModel):
    time_range: str = "24h"  # "1h", "24h", "7d", "30d"
    metrics: List[str] = ["cases", "performance", "errors"]
    filters: Optional[Dict[str, Any]] = None

class DashboardData(BaseModel):
    total_cases: int
    active_cases: int
    completed_cases: int
    avg_processing_time: float
    error_rate: float
    system_health: str
    recent_activities: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]

@router.get("/dashboard")
async def get_dashboard_data():
    """Real-time dashboard verilerini getir"""
    try:
        # Database bağlantısı
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        # Toplam case sayısı
        cursor.execute("SELECT COUNT(*) FROM workflow_cases")
        total_cases = cursor.fetchone()[0]
        
        # Aktif case sayısı
        cursor.execute("SELECT COUNT(*) FROM workflow_cases WHERE status IN ('created', 'processing', 'queued')")
        active_cases = cursor.fetchone()[0]
        
        # Tamamlanan case sayısı
        cursor.execute("SELECT COUNT(*) FROM workflow_cases WHERE status = 'completed'")
        completed_cases = cursor.fetchone()[0]
        
        # Son aktiviteler
        cursor.execute("""
            SELECT case_id, patient_id, status, created_at, updated_at 
            FROM workflow_cases 
            ORDER BY updated_at DESC 
            LIMIT 10
        """)
        recent_activities = []
        for row in cursor.fetchall():
            recent_activities.append({
                "case_id": row[0],
                "patient_id": row[1],
                "status": row[2],
                "created_at": row[3],
                "updated_at": row[4]
            })
        
        # Workflow steps analizi
        cursor.execute("""
            SELECT step_name, status, COUNT(*) as count
            FROM workflow_steps 
            GROUP BY step_name, status
        """)
        step_analysis = {}
        for row in cursor.fetchall():
            step_name, status, count = row
            if step_name not in step_analysis:
                step_analysis[step_name] = {}
            step_analysis[step_name][status] = count
        
        conn.close()
        
        # Mock performance metrics
        performance_metrics = {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 23.1,
            "network_io": 12.5,
            "api_response_time": 0.245,
            "error_rate": 2.1
        }
        
        # System health hesaplama
        system_health = "healthy"
        if performance_metrics["error_rate"] > 5:
            system_health = "warning"
        elif performance_metrics["error_rate"] > 10:
            system_health = "critical"
        
        dashboard_data = DashboardData(
            total_cases=total_cases,
            active_cases=active_cases,
            completed_cases=completed_cases,
            avg_processing_time=125.5,  # Mock data
            error_rate=performance_metrics["error_rate"],
            system_health=system_health,
            recent_activities=recent_activities,
            performance_metrics=performance_metrics
        )
        
        return {
            "status": "success",
            "data": dashboard_data.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Dashboard data error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dashboard data error: {str(e)}")

@router.get("/metrics/trends")
async def get_metrics_trends(time_range: str = "24h"):
    """Metrik trendlerini getir"""
    try:
        # Mock trend data
        trends = {
            "cases_per_hour": [2, 3, 1, 4, 2, 5, 3, 2, 1, 4, 3, 2],
            "processing_times": [120, 135, 110, 145, 130, 125, 140, 115, 120, 135, 130, 125],
            "error_rates": [1.2, 2.1, 0.8, 3.2, 1.5, 2.8, 1.9, 1.1, 2.3, 1.7, 2.0, 1.8],
            "system_load": [45, 52, 38, 67, 48, 55, 62, 41, 49, 58, 53, 46]
        }
        
        return {
            "status": "success",
            "time_range": time_range,
            "trends": trends,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Trends error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Trends error: {str(e)}")

@router.get("/alerts")
async def get_system_alerts():
    """Sistem uyarılarını getir"""
    try:
        alerts = []
        
        # Mock alert data
        if datetime.now().hour > 22:  # Gece saatleri
            alerts.append({
                "type": "warning",
                "message": "High system load detected during off-hours",
                "timestamp": datetime.now().isoformat(),
                "severity": "medium"
            })
        
        # Database kontrolü
        conn = sqlite3.connect('backend/neuropetrix_workflow.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM workflow_cases WHERE status = 'failed'")
        failed_cases = cursor.fetchone()[0]
        conn.close()
        
        if failed_cases > 0:
            alerts.append({
                "type": "error",
                "message": f"{failed_cases} failed cases detected",
                "timestamp": datetime.now().isoformat(),
                "severity": "high"
            })
        
        return {
            "status": "success",
            "alerts": alerts,
            "total_alerts": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Alerts error: {str(e)}")

@router.post("/export")
async def export_analytics_data(request: AnalyticsRequest):
    """Analytics verilerini export et"""
    try:
        # Mock export data
        export_data = {
            "export_id": f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "time_range": request.time_range,
            "metrics": request.metrics,
            "data": {
                "cases": 25,
                "performance": {"avg_time": 125.5, "success_rate": 97.9},
                "errors": {"total": 2, "rate": 2.1}
            },
            "exported_at": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "export_data": export_data,
            "download_url": f"/analytics/download/{export_data['export_id']}"
        }
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.get("/health")
async def analytics_health():
    """Analytics servis sağlığı"""
    return {
        "status": "healthy",
        "service": "analytics",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
