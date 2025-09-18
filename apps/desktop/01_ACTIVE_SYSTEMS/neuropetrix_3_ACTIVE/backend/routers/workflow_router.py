"""
Workflow Router - İncele → Onayla → Finalize API'leri
Role-based access control ile workflow yönetimi
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from backend.core.workflow_engine import (
    workflow_engine, WorkflowStatus, UserRole, WorkflowAction,
    WorkflowInstance, WorkflowStep, User
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/workflow", tags=["Workflow Management"])

class CreateWorkflowRequest(BaseModel):
    """Workflow Oluşturma İsteği"""
    report_id: str = Field(..., description="Rapor ID")
    title: str = Field(..., description="Workflow başlığı")
    template: str = Field("standard_report", description="Workflow şablonu")
    created_by: str = Field(..., description="Oluşturan kullanıcı ID")

class ExecuteActionRequest(BaseModel):
    """Aksiyon Çalıştırma İsteği"""
    action: str = Field(..., description="Çalıştırılacak aksiyon")
    user_id: str = Field(..., description="Kullanıcı ID")
    comment: Optional[str] = Field(None, description="Yorum")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Ek veriler")

class WorkflowResponse(BaseModel):
    """Workflow Yanıtı"""
    success: bool
    workflow_id: str
    message: str
    data: Optional[Dict[str, Any]] = None

class WorkflowStatusResponse(BaseModel):
    """Workflow Durum Yanıtı"""
    success: bool
    workflow: Dict[str, Any]
    available_actions: List[str]
    message: str

@router.get("/health")
async def workflow_health():
    """Workflow servis sağlık kontrolü"""
    return {
        "status": "healthy",
        "service": "Workflow Engine",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "active_workflows": len(workflow_engine.workflows),
        "registered_users": len(workflow_engine.users)
    }

@router.post("/create", response_model=WorkflowResponse)
async def create_workflow(request: CreateWorkflowRequest):
    """Yeni workflow oluştur"""
    try:
        logger.info(f"Workflow oluşturuluyor - Rapor: {request.report_id}")
        
        # Workflow oluştur
        workflow = workflow_engine.create_workflow(
            report_id=request.report_id,
            title=request.title,
            template=request.template,
            created_by=request.created_by
        )
        
        # Workflow durumunu al
        workflow_status = workflow_engine.get_workflow_status(workflow.workflow_id)
        
        return WorkflowResponse(
            success=True,
            workflow_id=workflow.workflow_id,
            message="Workflow başarıyla oluşturuldu",
            data=workflow_status
        )
        
    except Exception as e:
        logger.error(f"Workflow oluşturma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow oluşturulamadı: {str(e)}"
        )

@router.post("/{workflow_id}/execute", response_model=WorkflowResponse)
async def execute_workflow_action(workflow_id: str, request: ExecuteActionRequest):
    """Workflow aksiyonu çalıştır"""
    try:
        logger.info(f"Workflow aksiyonu çalıştırılıyor - {workflow_id}: {request.action}")
        
        # Aksiyonu çalıştır
        action = WorkflowAction(request.action)
        success = workflow_engine.execute_action(
            workflow_id=workflow_id,
            action=action,
            user_id=request.user_id,
            comment=request.comment,
            metadata=request.metadata
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aksiyon çalıştırılamadı - yetki veya durum hatası"
            )
        
        # Güncel durumu al
        workflow_status = workflow_engine.get_workflow_status(workflow_id)
        available_actions = workflow_engine.get_available_actions(workflow_id, request.user_id)
        
        return WorkflowResponse(
            success=True,
            workflow_id=workflow_id,
            message=f"Aksiyon {request.action} başarıyla çalıştırıldı",
            data={
                "workflow": workflow_status,
                "available_actions": available_actions
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz aksiyon: {request.action}"
        )
    except Exception as e:
        logger.error(f"Workflow aksiyonu hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Aksiyon çalıştırılamadı: {str(e)}"
        )

@router.get("/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str, user_id: str):
    """Workflow durumunu getir"""
    try:
        # Workflow durumunu al
        workflow_status = workflow_engine.get_workflow_status(workflow_id)
        
        if not workflow_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow bulunamadı"
            )
        
        # Kullanıcının yapabileceği aksiyonları al
        available_actions = workflow_engine.get_available_actions(workflow_id, user_id)
        
        return WorkflowStatusResponse(
            success=True,
            workflow=workflow_status,
            available_actions=available_actions,
            message="Workflow durumu başarıyla alındı"
        )
        
    except Exception as e:
        logger.error(f"Workflow durumu alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow durumu alınamadı: {str(e)}"
        )

@router.get("/user/{user_id}/workflows")
async def get_user_workflows(user_id: str):
    """Kullanıcının workflow'larını getir"""
    try:
        workflows = workflow_engine.get_user_workflows(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "workflows": workflows,
            "count": len(workflows),
            "message": f"{len(workflows)} workflow bulundu"
        }
        
    except Exception as e:
        logger.error(f"Kullanıcı workflow'ları alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kullanıcı workflow'ları alınamadı: {str(e)}"
        )

@router.get("/templates")
async def get_workflow_templates():
    """Workflow şablonlarını getir"""
    try:
        templates = workflow_engine.get_workflow_templates()
        
        return {
            "success": True,
            "templates": templates,
            "count": len(templates),
            "message": "Workflow şablonları başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Workflow şablonları alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow şablonları alınamadı: {str(e)}"
        )

@router.get("/users")
async def get_users():
    """Kullanıcıları getir"""
    try:
        users = workflow_engine.get_users()
        
        return {
            "success": True,
            "users": users,
            "count": len(users),
            "message": "Kullanıcılar başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Kullanıcılar alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kullanıcılar alınamadı: {str(e)}"
        )

@router.get("/actions")
async def get_available_actions():
    """Mevcut aksiyonları getir"""
    try:
        actions = [
            {
                "action": action.value,
                "name": _get_action_name(action),
                "description": _get_action_description(action)
            }
            for action in WorkflowAction
        ]
        
        return {
            "success": True,
            "actions": actions,
            "count": len(actions),
            "message": "Mevcut aksiyonlar başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Aksiyonlar alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Aksiyonlar alınamadı: {str(e)}"
        )

@router.get("/roles")
async def get_user_roles():
    """Kullanıcı rollerini getir"""
    try:
        roles = [
            {
                "role": role.value,
                "name": _get_role_name(role),
                "description": _get_role_description(role),
                "permissions": _get_role_permissions(role)
            }
            for role in UserRole
        ]
        
        return {
            "success": True,
            "roles": roles,
            "count": len(roles),
            "message": "Kullanıcı rolleri başarıyla alındı"
        }
        
    except Exception as e:
        logger.error(f"Roller alma hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Roller alınamadı: {str(e)}"
        )

@router.post("/{workflow_id}/quick-actions")
async def execute_quick_action(
    workflow_id: str,
    action: str,
    user_id: str,
    comment: Optional[str] = None
):
    """Hızlı eylemler - Danışmanlık iste, Paylaş, Raporu sonlandır"""
    try:
        logger.info(f"Hızlı eylem çalıştırılıyor - {workflow_id}: {action}")
        
        # Hızlı eylemleri map et
        action_mapping = {
            "request_consultation": WorkflowAction.REQUEST_CONSULTATION,
            "share": WorkflowAction.COMMENT,
            "finalize_report": WorkflowAction.FINALIZE,
            "approve": WorkflowAction.APPROVE,
            "reject": WorkflowAction.REJECT
        }
        
        if action not in action_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Geçersiz hızlı eylem: {action}"
            )
        
        workflow_action = action_mapping[action]
        
        # Aksiyonu çalıştır
        success = workflow_engine.execute_action(
            workflow_id=workflow_id,
            action=workflow_action,
            user_id=user_id,
            comment=comment
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hızlı eylem çalıştırılamadı - yetki veya durum hatası"
            )
        
        # Güncel durumu al
        workflow_status = workflow_engine.get_workflow_status(workflow_id)
        
        return {
            "success": True,
            "action": action,
            "workflow_id": workflow_id,
            "workflow": workflow_status,
            "message": f"Hızlı eylem {action} başarıyla çalıştırıldı"
        }
        
    except Exception as e:
        logger.error(f"Hızlı eylem hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hızlı eylem çalıştırılamadı: {str(e)}"
        )

# Helper functions
def _get_action_name(action: WorkflowAction) -> str:
    """Aksiyon ismini getir"""
    names = {
        WorkflowAction.CREATE: "Oluştur",
        WorkflowAction.REVIEW: "İncele",
        WorkflowAction.APPROVE: "Onayla",
        WorkflowAction.REJECT: "Reddet",
        WorkflowAction.FINALIZE: "Finalize Et",
        WorkflowAction.ARCHIVE: "Arşivle",
        WorkflowAction.COMMENT: "Yorum Ekle",
        WorkflowAction.REQUEST_CONSULTATION: "Danışmanlık İste"
    }
    return names.get(action, action.value)

def _get_action_description(action: WorkflowAction) -> str:
    """Aksiyon açıklamasını getir"""
    descriptions = {
        WorkflowAction.CREATE: "Yeni rapor oluştur",
        WorkflowAction.REVIEW: "Raporu incele ve yorum ekle",
        WorkflowAction.APPROVE: "Raporu onayla",
        WorkflowAction.REJECT: "Raporu reddet",
        WorkflowAction.FINALIZE: "Raporu finalize et",
        WorkflowAction.ARCHIVE: "Raporu arşivle",
        WorkflowAction.COMMENT: "Raporu paylaş veya yorum ekle",
        WorkflowAction.REQUEST_CONSULTATION: "Danışmanlık iste"
    }
    return descriptions.get(action, "")

def _get_role_name(role: UserRole) -> str:
    """Rol ismini getir"""
    names = {
        UserRole.RADIOLOGIST: "Radyolog",
        UserRole.CLINICIAN: "Klinisyen",
        UserRole.ADMIN: "Yönetici",
        UserRole.TECHNICIAN: "Teknisyen",
        UserRole.VIEWER: "Görüntüleyici"
    }
    return names.get(role, role.value)

def _get_role_description(role: UserRole) -> str:
    """Rol açıklamasını getir"""
    descriptions = {
        UserRole.RADIOLOGIST: "Radyoloji uzmanı - rapor oluşturma ve inceleme yetkisi",
        UserRole.CLINICIAN: "Klinik uzman - rapor onaylama yetkisi",
        UserRole.ADMIN: "Sistem yöneticisi - tüm yetkiler",
        UserRole.TECHNICIAN: "Teknik personel - sınırlı yetkiler",
        UserRole.VIEWER: "Görüntüleyici - sadece okuma yetkisi"
    }
    return descriptions.get(role, "")

def _get_role_permissions(role: UserRole) -> List[str]:
    """Rol yetkilerini getir"""
    permissions = {
        UserRole.RADIOLOGIST: ["create", "review", "approve", "comment", "request_consultation"],
        UserRole.CLINICIAN: ["approve", "reject", "comment", "request_consultation"],
        UserRole.ADMIN: ["create", "review", "approve", "reject", "finalize", "archive", "comment"],
        UserRole.TECHNICIAN: ["comment"],
        UserRole.VIEWER: []
    }
    return permissions.get(role, [])

# Test endpoint
@router.get("/test")
async def test_workflow_engine():
    """Workflow engine test"""
    try:
        # Test workflow oluştur
        workflow = workflow_engine.create_workflow(
            report_id="TEST_001",
            title="Test Raporu",
            template="standard_report",
            created_by="rad_001"
        )
        
        # Test aksiyonları
        workflow_engine.execute_action(workflow.workflow_id, WorkflowAction.REVIEW, "rad_001", "Test inceleme")
        workflow_engine.execute_action(workflow.workflow_id, WorkflowAction.APPROVE, "clin_001", "Test onay")
        
        # Durumu kontrol et
        status = workflow_engine.get_workflow_status(workflow.workflow_id)
        
        return {
            "success": True,
            "test_workflow": status,
            "message": "Workflow engine test başarılı"
        }
        
    except Exception as e:
        logger.error(f"Workflow engine test hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow engine test başarısız: {str(e)}"
        )
