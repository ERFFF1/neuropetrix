from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Any, Optional
import json
import asyncio
import logging
from datetime import datetime
import sqlite3

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket Real-time"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, List[WebSocket]] = {}
        self.case_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str = None, case_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
        
        if case_id:
            if case_id not in self.case_connections:
                self.case_connections[case_id] = []
            self.case_connections[case_id].append(websocket)
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: str = None, case_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        if case_id and case_id in self.case_connections:
            if websocket in self.case_connections[case_id]:
                self.case_connections[case_id].remove(websocket)
            if not self.case_connections[case_id]:
                del self.case_connections[case_id]
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def send_to_user(self, message: str, user_id: str):
        if user_id in self.user_connections:
            disconnected = []
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection, user_id=user_id)

    async def send_to_case(self, message: str, case_id: str):
        if case_id in self.case_connections:
            disconnected = []
            for connection in self.case_connections[case_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending to case {case_id}: {e}")
                    disconnected.append(connection)
            
                    # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, case_id=case_id)
    
    async def broadcast_notification(self, notification: dict):
        """Tüm bağlantılara bildirim gönder"""
        message = {
            "type": "notification",
            "data": notification,
            "timestamp": datetime.now().isoformat()
        }
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, user_id: str = None, case_id: str = None):
    await manager.connect(websocket, user_id, case_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}),
                    websocket
                )
            elif message_data.get("type") == "subscribe_case":
                case_id = message_data.get("case_id")
                if case_id:
                    await manager.connect(websocket, case_id=case_id)
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "subscribed",
                            "case_id": case_id,
                            "message": f"Subscribed to case {case_id}"
                        }),
                        websocket
                    )
            elif message_data.get("type") == "get_case_status":
                case_id = message_data.get("case_id")
                if case_id:
                    # Get case status from database
                    try:
                        conn = sqlite3.connect('neuropetrix_workflow.db')
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT case_id, patient_id, status, created_at, updated_at 
                            FROM workflow_cases 
                            WHERE case_id = ?
                        """, (case_id,))
                        row = cursor.fetchone()
                        conn.close()
                        
                        if row:
                            case_data = {
                                "type": "case_status",
                                "case_id": row[0],
                                "patient_id": row[1],
                                "status": row[2],
                                "created_at": row[3],
                                "updated_at": row[4]
                            }
                            await manager.send_personal_message(
                                json.dumps(case_data),
                                websocket
                            )
                    except Exception as e:
                        logger.error(f"Error getting case status: {e}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id, case_id)

@router.websocket("/case/{case_id}")
async def case_websocket(websocket: WebSocket, case_id: str):
    await manager.connect(websocket, case_id=case_id)
    try:
        # Send initial case status
        try:
            conn = sqlite3.connect('neuropetrix_workflow.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT case_id, patient_id, status, created_at, updated_at 
                FROM workflow_cases 
                WHERE case_id = ?
            """, (case_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                case_data = {
                    "type": "case_status",
                    "case_id": row[0],
                    "patient_id": row[1],
                    "status": row[2],
                    "created_at": row[3],
                    "updated_at": row[4]
                }
                await manager.send_personal_message(
                    json.dumps(case_data),
                    websocket
                )
        except Exception as e:
            logger.error(f"Error getting initial case status: {e}")
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle case-specific messages
            if message_data.get("type") == "get_workflow_steps":
                try:
                    conn = sqlite3.connect('neuropetrix_workflow.db')
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT step_name, status, started_at, completed_at, error_message
                        FROM workflow_steps 
                        WHERE case_id = ?
                        ORDER BY started_at
                    """, (case_id,))
                    steps = []
                    for row in cursor.fetchall():
                        steps.append({
                            "step_name": row[0],
                            "status": row[1],
                            "started_at": row[2],
                            "completed_at": row[3],
                            "error_message": row[4]
                        })
                    conn.close()
                    
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "workflow_steps",
                            "case_id": case_id,
                            "steps": steps
                        }),
                        websocket
                    )
                except Exception as e:
                    logger.error(f"Error getting workflow steps: {e}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, case_id=case_id)

@router.websocket("/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial dashboard data
        try:
            conn = sqlite3.connect('neuropetrix_workflow.db')
            cursor = conn.cursor()
            
            # Get dashboard metrics
            cursor.execute("SELECT COUNT(*) FROM workflow_cases")
            total_cases = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM workflow_cases WHERE status IN ('created', 'processing', 'queued')")
            active_cases = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM workflow_cases WHERE status = 'completed'")
            completed_cases = cursor.fetchone()[0]
            
            conn.close()
            
            dashboard_data = {
                "type": "dashboard_update",
                "data": {
                    "total_cases": total_cases,
                    "active_cases": active_cases,
                    "completed_cases": completed_cases,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            await manager.send_personal_message(
                json.dumps(dashboard_data),
                websocket
            )
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle dashboard-specific messages
            if message_data.get("type") == "refresh_dashboard":
                # Send updated dashboard data
                try:
                    conn = sqlite3.connect('neuropetrix_workflow.db')
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM workflow_cases")
                    total_cases = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM workflow_cases WHERE status IN ('created', 'processing', 'queued')")
                    active_cases = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM workflow_cases WHERE status = 'completed'")
                    completed_cases = cursor.fetchone()[0]
                    
                    conn.close()
                    
                    dashboard_data = {
                        "type": "dashboard_update",
                        "data": {
                            "total_cases": total_cases,
                            "active_cases": active_cases,
                            "completed_cases": completed_cases,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                    
                    await manager.send_personal_message(
                        json.dumps(dashboard_data),
                        websocket
                    )
                except Exception as e:
                    logger.error(f"Error refreshing dashboard: {e}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Utility functions for sending real-time updates
async def send_case_update(case_id: str, update_data: Dict[str, Any]):
    """Send case update to all connected clients for this case"""
    message = {
        "type": "case_update",
        "case_id": case_id,
        "data": update_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.send_to_case(json.dumps(message), case_id)

async def send_workflow_progress(case_id: str, step_name: str, progress: int, status: str):
    """Send workflow progress update"""
    message = {
        "type": "workflow_progress",
        "case_id": case_id,
        "step_name": step_name,
        "progress": progress,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    await manager.send_to_case(json.dumps(message), case_id)

async def send_system_alert(alert_type: str, message: str, severity: str = "info"):
    """Send system-wide alert"""
    alert_data = {
        "type": "system_alert",
        "alert_type": alert_type,
        "message": message,
        "severity": severity,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(json.dumps(alert_data))

@router.get("/connections")
async def get_connection_stats():
    """Get WebSocket connection statistics"""
    return {
        "total_connections": len(manager.active_connections),
        "user_connections": {k: len(v) for k, v in manager.user_connections.items()},
        "case_connections": {k: len(v) for k, v in manager.case_connections.items()},
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def websocket_health():
    """WebSocket service health check"""
    return {
        "status": "healthy",
        "service": "websocket",
        "version": "1.0.0",
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }
