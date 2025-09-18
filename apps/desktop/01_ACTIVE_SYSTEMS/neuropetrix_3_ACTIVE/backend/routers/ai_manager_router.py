"""
AI Manager Router - Tüm AI modüllerini yöneten merkezi API
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from services.ai_manager import ai_manager, AIModuleType, AIStatus
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-manager", tags=["AI Manager"])

# Pydantic modelleri
class AITaskRequest(BaseModel):
    module_type: str
    task: str
    parameters: Optional[Dict[str, Any]] = None

class AIInsightRequest(BaseModel):
    context: Dict[str, Any]
    include_modules: Optional[List[str]] = None

class AIModuleStatusResponse(BaseModel):
    status: str
    capabilities: List[str]
    last_used: Optional[str]
    available: bool

@router.get("/status")
async def get_ai_manager_status():
    """AI Manager genel durumunu getir"""
    try:
        status = await ai_manager.get_all_modules_status()
        return {
            "success": True,
            "ai_manager": status,
            "message": "AI Manager durumu başarıyla alındı"
        }
    except Exception as e:
        logger.error(f"AI Manager status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Manager durumu alınamadı: {str(e)}")

@router.get("/modules/{module_type}/status")
async def get_module_status(module_type: str):
    """Belirli bir AI modülünün durumunu getir"""
    try:
        # Module type'ı validate et
        try:
            module_enum = AIModuleType(module_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Geçersiz modül tipi: {module_type}")
        
        status = await ai_manager.get_module_status(module_enum)
        return {
            "success": True,
            "module": module_type,
            "status": status,
            "message": f"{module_type} modülü durumu alındı"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Module status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Modül durumu alınamadı: {str(e)}")

@router.post("/execute-task")
async def execute_ai_task(request: AITaskRequest, background_tasks: BackgroundTasks):
    """AI görevini çalıştır"""
    try:
        # Module type'ı validate et
        try:
            module_enum = AIModuleType(request.module_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Geçersiz modül tipi: {request.module_type}")
        
        # Görevi çalıştır
        result = await ai_manager.execute_ai_task(
            module_enum, 
            request.task, 
            **(request.parameters or {})
        )
        
        return {
            "success": result.get("success", False),
            "result": result,
            "message": f"{request.module_type} modülünde {request.task} görevi çalıştırıldı"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI task execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI görevi çalıştırılamadı: {str(e)}")

@router.post("/insights")
async def get_ai_insights(request: AIInsightRequest):
    """AI modüllerinden içgörüler al"""
    try:
        insights = await ai_manager.get_ai_insights(request.context)
        return {
            "success": True,
            "insights": insights,
            "message": "AI içgörüleri başarıyla alındı"
        }
    except Exception as e:
        logger.error(f"AI insights error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI içgörüleri alınamadı: {str(e)}")

@router.get("/capabilities")
async def get_ai_capabilities():
    """Tüm AI modüllerinin yeteneklerini getir"""
    try:
        capabilities = {}
        for module_type, module_data in ai_manager.modules.items():
            capabilities[module_type.value] = {
                "capabilities": module_data["capabilities"],
                "status": module_data["status"].value,
                "available": module_data["status"] == AIStatus.AVAILABLE
            }
        
        return {
            "success": True,
            "capabilities": capabilities,
            "message": "AI yetenekleri başarıyla alındı"
        }
    except Exception as e:
        logger.error(f"AI capabilities error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI yetenekleri alınamadı: {str(e)}")

@router.get("/health")
async def ai_health_check():
    """AI sistem sağlık kontrolü"""
    try:
        status = await ai_manager.get_all_modules_status()
        healthy_modules = status["available_modules"]
        total_modules = status["total_modules"]
        
        health_score = (healthy_modules / total_modules) * 100 if total_modules > 0 else 0
        
        return {
            "success": True,
            "health": {
                "score": health_score,
                "healthy_modules": healthy_modules,
                "total_modules": total_modules,
                "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "unhealthy"
            },
            "message": f"AI sistem sağlığı: {health_score:.1f}%"
        }
    except Exception as e:
        logger.error(f"AI health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI sağlık kontrolü yapılamadı: {str(e)}")

@router.get("/modules")
async def list_ai_modules():
    """Tüm AI modüllerini listele"""
    try:
        modules = []
        for module_type, module_data in ai_manager.modules.items():
            modules.append({
                "name": module_type.value,
                "display_name": module_type.value.replace("_", " ").title(),
                "status": module_data["status"].value,
                "capabilities": module_data["capabilities"],
                "last_used": module_data["last_used"]
            })
        
        return {
            "success": True,
            "modules": modules,
            "count": len(modules),
            "message": f"{len(modules)} AI modülü listelendi"
        }
    except Exception as e:
        logger.error(f"AI modules list error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI modülleri listelenemedi: {str(e)}")

@router.post("/test-module/{module_type}")
async def test_ai_module(module_type: str):
    """AI modülünü test et"""
    try:
        # Module type'ı validate et
        try:
            module_enum = AIModuleType(module_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Geçersiz modül tipi: {module_type}")
        
        # Test görevi çalıştır
        test_result = await ai_manager.execute_ai_task(module_enum, "test")
        
        return {
            "success": test_result.get("success", False),
            "test_result": test_result,
            "module": module_type,
            "message": f"{module_type} modülü test edildi"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI module test error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI modülü test edilemedi: {str(e)}")
