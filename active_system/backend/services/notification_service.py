"""
Real-time Notification Service
NeuroPETRIX - Real-time bildirim sistemi
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Bildirim türleri"""
    CASE_CREATED = "case_created"
    CASE_UPDATED = "case_updated"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANALYSIS_FAILED = "analysis_failed"
    SYSTEM_ALERT = "system_alert"
    USER_MESSAGE = "user_message"

class NotificationPriority(Enum):
    """Bildirim öncelikleri"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Notification:
    """Bildirim modeli"""
    
    def __init__(self, 
                 id: str,
                 type: NotificationType,
                 title: str,
                 message: str,
                 priority: NotificationPriority = NotificationPriority.NORMAL,
                 user_id: Optional[str] = None,
                 case_id: Optional[str] = None,
                 data: Optional[Dict[str, Any]] = None):
        self.id = id
        self.type = type
        self.title = title
        self.message = message
        self.priority = priority
        self.user_id = user_id
        self.case_id = case_id
        self.data = data or {}
        self.created_at = datetime.now()
        self.read = False
        self.read_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Bildirimi dictionary'e çevir"""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value,
            "user_id": self.user_id,
            "case_id": self.case_id,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "read": self.read,
            "read_at": self.read_at.isoformat() if self.read_at else None
        }

class NotificationService:
    """Bildirim servisi"""
    
    def __init__(self):
        self.notifications: Dict[str, Notification] = {}
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}
        self.user_notifications: Dict[str, List[str]] = {}
    
    async def create_notification(self, 
                                type: NotificationType,
                                title: str,
                                message: str,
                                priority: NotificationPriority = NotificationPriority.NORMAL,
                                user_id: Optional[str] = None,
                                case_id: Optional[str] = None,
                                data: Optional[Dict[str, Any]] = None) -> Notification:
        """Yeni bildirim oluştur"""
        try:
            notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.notifications)}"
            
            notification = Notification(
                id=notification_id,
                type=type,
                title=title,
                message=message,
                priority=priority,
                user_id=user_id,
                case_id=case_id,
                data=data
            )
            
            # Bildirimi kaydet
            self.notifications[notification_id] = notification
            
            # Kullanıcı bildirimlerine ekle
            if user_id:
                if user_id not in self.user_notifications:
                    self.user_notifications[user_id] = []
                self.user_notifications[user_id].append(notification_id)
            
            # Abonelere gönder
            await self._broadcast_notification(notification)
            
            logger.info(f"Bildirim oluşturuldu: {notification_id} - {title}")
            return notification
            
        except Exception as e:
            logger.error(f"Bildirim oluşturulamadı: {e}")
            raise
    
    async def _broadcast_notification(self, notification: Notification):
        """Bildirimi abonelere gönder"""
        try:
            # Tüm abonelere gönder
            for user_id, queues in self.subscribers.items():
                if notification.user_id is None or notification.user_id == user_id:
                    for queue in queues:
                        try:
                            await queue.put(notification.to_dict())
                        except Exception as e:
                            logger.error(f"Bildirim gönderilemedi: {e}")
            
            # WebSocket abonelere gönder
            await self._send_websocket_notification(notification)
            
        except Exception as e:
            logger.error(f"Bildirim yayınlanamadı: {e}")
    
    async def _send_websocket_notification(self, notification: Notification):
        """WebSocket ile bildirim gönder"""
        try:
            # WebSocket manager'a bildirim gönder
            from backend.routers.websocket_router import websocket_manager
            if websocket_manager:
                await websocket_manager.broadcast_notification(notification.to_dict())
        except Exception as e:
            logger.error(f"WebSocket bildirimi gönderilemedi: {e}")
    
    async def subscribe(self, user_id: str) -> asyncio.Queue:
        """Kullanıcı için bildirim aboneliği oluştur"""
        try:
            queue = asyncio.Queue()
            
            if user_id not in self.subscribers:
                self.subscribers[user_id] = []
            
            self.subscribers[user_id].append(queue)
            
            logger.info(f"Kullanıcı abone oldu: {user_id}")
            return queue
            
        except Exception as e:
            logger.error(f"Abonelik oluşturulamadı: {e}")
            raise
    
    async def unsubscribe(self, user_id: str, queue: asyncio.Queue):
        """Kullanıcı aboneliğini iptal et"""
        try:
            if user_id in self.subscribers:
                if queue in self.subscribers[user_id]:
                    self.subscribers[user_id].remove(queue)
                
                if not self.subscribers[user_id]:
                    del self.subscribers[user_id]
            
            logger.info(f"Kullanıcı aboneliği iptal edildi: {user_id}")
            
        except Exception as e:
            logger.error(f"Abonelik iptal edilemedi: {e}")
    
    def get_user_notifications(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Kullanıcının bildirimlerini getir"""
        try:
            if user_id not in self.user_notifications:
                return []
            
            notification_ids = self.user_notifications[user_id][-limit:]
            notifications = []
            
            for notification_id in notification_ids:
                if notification_id in self.notifications:
                    notifications.append(self.notifications[notification_id].to_dict())
            
            return notifications
            
        except Exception as e:
            logger.error(f"Kullanıcı bildirimleri getirilemedi: {e}")
            return []
    
    def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """Bildirimi okundu olarak işaretle"""
        try:
            if notification_id in self.notifications:
                notification = self.notifications[notification_id]
                if notification.user_id == user_id:
                    notification.read = True
                    notification.read_at = datetime.now()
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Bildirim okundu işaretlenemedi: {e}")
            return False
    
    def get_unread_count(self, user_id: str) -> int:
        """Kullanıcının okunmamış bildirim sayısını getir"""
        try:
            if user_id not in self.user_notifications:
                return 0
            
            unread_count = 0
            for notification_id in self.user_notifications[user_id]:
                if notification_id in self.notifications:
                    notification = self.notifications[notification_id]
                    if not notification.read:
                        unread_count += 1
            
            return unread_count
            
        except Exception as e:
            logger.error(f"Okunmamış bildirim sayısı getirilemedi: {e}")
            return 0

# Singleton instance
notification_service = NotificationService()
