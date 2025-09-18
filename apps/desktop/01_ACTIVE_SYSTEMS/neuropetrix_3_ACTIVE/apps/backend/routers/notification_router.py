"""
Notification Router
NeuroPETRIX - Real-time bildirim API'leri
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from services.notification_service import notification_service, NotificationType, NotificationPriority

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Pydantic Models
class NotificationCreateRequest(BaseModel):
    type: str
    title: str
    message: str
    priority: str = "normal"
    user_id: Optional[str] = None
    case_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    priority: str
    user_id: Optional[str]
    case_id: Optional[str]
    data: Dict[str, Any]
    created_at: str
    read: bool
    read_at: Optional[str]

@router.post("/create", response_model=NotificationResponse)
async def create_notification(request: NotificationCreateRequest):
    """Yeni bildirim oluştur"""
    try:
        # Notification type ve priority'yi enum'a çevir
        try:
            notification_type = NotificationType(request.type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Geçersiz bildirim türü: {request.type}"
            )
        
        try:
            priority = NotificationPriority(request.priority)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Geçersiz öncelik: {request.priority}"
            )
        
        # Bildirim oluştur
        notification = await notification_service.create_notification(
            type=notification_type,
            title=request.title,
            message=request.message,
            priority=priority,
            user_id=request.user_id,
            case_id=request.case_id,
            data=request.data
        )
        
        return NotificationResponse(**notification.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bildirim oluşturulamadı: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bildirim oluşturulamadı: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[NotificationResponse])
async def get_user_notifications(user_id: str, limit: int = 50):
    """Kullanıcının bildirimlerini getir"""
    try:
        notifications = notification_service.get_user_notifications(user_id, limit)
        return [NotificationResponse(**notif) for notif in notifications]
        
    except Exception as e:
        logger.error(f"Kullanıcı bildirimleri getirilemedi: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kullanıcı bildirimleri getirilemedi: {str(e)}"
        )

@router.put("/{notification_id}/read")
async def mark_notification_as_read(notification_id: str, user_id: str):
    """Bildirimi okundu olarak işaretle"""
    try:
        success = notification_service.mark_as_read(user_id, notification_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bildirim bulunamadı veya kullanıcıya ait değil"
            )
        
        return {"status": "success", "message": "Bildirim okundu olarak işaretlendi"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bildirim okundu işaretlenemedi: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bildirim okundu işaretlenemedi: {str(e)}"
        )

@router.get("/user/{user_id}/unread-count")
async def get_unread_count(user_id: str):
    """Kullanıcının okunmamış bildirim sayısını getir"""
    try:
        count = notification_service.get_unread_count(user_id)
        return {"user_id": user_id, "unread_count": count}
        
    except Exception as e:
        logger.error(f"Okunmamış bildirim sayısı getirilemedi: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Okunmamış bildirim sayısı getirilemedi: {str(e)}"
        )

@router.websocket("/subscribe/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """WebSocket ile bildirim aboneliği"""
    try:
        # WebSocket bağlantısını kabul et
        await websocket.accept()
        
        # Bildirim aboneliği oluştur
        queue = await notification_service.subscribe(user_id)
        
        logger.info(f"Kullanıcı bildirim aboneliği başladı: {user_id}")
        
        try:
            while True:
                # Bildirim bekle
                notification = await queue.get()
                
                # WebSocket'e gönder
                await websocket.send_text(str(notification))
                
        except WebSocketDisconnect:
            logger.info(f"Kullanıcı bildirim aboneliği sonlandı: {user_id}")
        except Exception as e:
            logger.error(f"WebSocket bildirim hatası: {e}")
        finally:
            # Aboneliği iptal et
            await notification_service.unsubscribe(user_id, queue)
            
    except Exception as e:
        logger.error(f"WebSocket bildirim aboneliği hatası: {e}")
        try:
            await websocket.close()
        except:
            pass

@router.get("/health")
async def health_check():
    """Bildirim servis sağlık kontrolü"""
    return {
        "status": "healthy",
        "service": "notifications",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "active_subscribers": len(notification_service.subscribers),
        "total_notifications": len(notification_service.notifications)
    }