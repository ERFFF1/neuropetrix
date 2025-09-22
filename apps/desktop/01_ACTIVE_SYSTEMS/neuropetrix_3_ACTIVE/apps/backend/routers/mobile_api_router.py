from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json
import logging
from datetime import datetime
import sqlite3
import hashlib
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile", tags=["Mobile API"])

class MobileLoginRequest(BaseModel):
    username: str
    password: str
    device_id: str
    device_type: str = "mobile"  # "mobile", "tablet", "web"

class MobileLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    expires_in: int
    user_info: Dict[str, Any]

class MobileCaseRequest(BaseModel):
    patient_id: str
    case_type: str
    priority: str = "normal"
    location: Optional[Dict[str, float]] = None  # GPS coordinates
    notes: Optional[str] = None

class MobileNotificationRequest(BaseModel):
    user_id: str
    notification_type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None

class MobileSyncRequest(BaseModel):
    last_sync: str
    device_id: str

# Mock user database
MOCK_USERS = {
    "doctor1": {
        "password": "password123",
        "user_id": "user_001",
        "name": "Dr. John Smith",
        "role": "radiologist",
        "department": "Radiology",
        "permissions": ["read_cases", "create_cases", "approve_reports"]
    },
    "nurse1": {
        "password": "nurse123",
        "user_id": "user_002", 
        "name": "Nurse Jane Doe",
        "role": "nurse",
        "department": "Oncology",
        "permissions": ["read_cases", "update_patient_info"]
    }
}

# Mock device tokens for push notifications
DEVICE_TOKENS = {}

@router.post("/auth/login", response_model=MobileLoginResponse)
async def mobile_login(request: MobileLoginRequest):
    """Mobile app login endpoint"""
    try:
        # Validate credentials
        if request.username not in MOCK_USERS:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = MOCK_USERS[request.username]
        if user["password"] != request.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate tokens
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        
        # Store device info
        device_key = f"{request.username}_{request.device_id}"
        DEVICE_TOKENS[device_key] = {
            "device_id": request.device_id,
            "device_type": request.device_type,
            "last_seen": datetime.now().isoformat(),
            "access_token": access_token
        }
        
        # Store login in database
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mobile_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                device_id TEXT,
                access_token TEXT,
                refresh_token TEXT,
                created_at TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        cursor.execute("""
            INSERT INTO mobile_sessions 
            (user_id, device_id, access_token, refresh_token, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user["user_id"],
            request.device_id,
            access_token,
            refresh_token,
            datetime.now().isoformat(),
            (datetime.now().timestamp() + 3600)  # 1 hour expiry
        ))
        
        conn.commit()
        conn.close()
        
        return MobileLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user["user_id"],
            expires_in=3600,
            user_info={
                "name": user["name"],
                "role": user["role"],
                "department": user["department"],
                "permissions": user["permissions"]
            }
        )
        
    except Exception as e:
        logger.error(f"Mobile login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@router.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, device_id FROM mobile_sessions 
            WHERE refresh_token = ? AND is_active = 1
        """, (refresh_token,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user_id, device_id = row
        
        # Generate new access token
        new_access_token = secrets.token_urlsafe(32)
        
        # Update session
        cursor.execute("""
            UPDATE mobile_sessions 
            SET access_token = ?, expires_at = ?
            WHERE refresh_token = ?
        """, (
            new_access_token,
            datetime.now().timestamp() + 3600,
            refresh_token
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "access_token": new_access_token,
            "expires_in": 3600,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Token refresh error: {str(e)}")

@router.post("/auth/logout")
async def mobile_logout(access_token: str):
    """Mobile app logout"""
    try:
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE mobile_sessions 
            SET is_active = 0 
            WHERE access_token = ?
        """, (access_token,))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "Logged out successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Logout error: {str(e)}")

@router.get("/cases")
async def get_mobile_cases(access_token: str, limit: int = 20, status: str = None):
    """Get cases for mobile app"""
    try:
        # Validate token
        user_id = await validate_mobile_token(access_token)
        
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        query = "SELECT * FROM workflow_cases"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        cases = []
        for row in cursor.fetchall():
            cases.append({
                "case_id": row[0],
                "patient_id": row[1],
                "purpose": row[2],
                "icd_code": row[3],
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6],
                "metadata": json.loads(row[7]) if row[7] else {}
            })
        
        conn.close()
        
        return {
            "status": "success",
            "cases": cases,
            "total": len(cases),
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get mobile cases error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get mobile cases error: {str(e)}")

@router.get("/cases/{case_id}")
async def get_mobile_case_detail(case_id: str, access_token: str):
    """Get detailed case information for mobile"""
    try:
        # Validate token
        user_id = await validate_mobile_token(access_token)
        
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        # Get case info
        cursor.execute("""
            SELECT * FROM workflow_cases WHERE case_id = ?
        """, (case_id,))
        
        case_row = cursor.fetchone()
        if not case_row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Get workflow steps
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
        
        case_detail = {
            "case_id": case_row[0],
            "patient_id": case_row[1],
            "purpose": case_row[2],
            "icd_code": case_row[3],
            "status": case_row[4],
            "created_at": case_row[5],
            "updated_at": case_row[6],
            "metadata": json.loads(case_row[7]) if case_row[7] else {},
            "workflow_steps": steps
        }
        
        return {
            "status": "success",
            "case": case_detail,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get mobile case detail error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get mobile case detail error: {str(e)}")

@router.post("/cases/create")
async def create_mobile_case(request: MobileCaseRequest, access_token: str):
    """Create new case from mobile app"""
    try:
        # Validate token
        user_id = await validate_mobile_token(access_token)
        
        # Generate case ID
        case_id = f"CASE-MOBILE-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create case
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO workflow_cases 
            (case_id, patient_id, purpose, icd_code, status, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            case_id,
            request.patient_id,
            request.case_type,
            "Z00.0",  # Default ICD code
            "created",
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            json.dumps({
                "created_by": user_id,
                "priority": request.priority,
                "location": request.location,
                "notes": request.notes,
                "source": "mobile_app"
            })
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "case_id": case_id,
            "message": "Case created successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Create mobile case error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Create mobile case error: {str(e)}")

@router.get("/notifications")
async def get_mobile_notifications(access_token: str, limit: int = 20):
    """Get notifications for mobile app"""
    try:
        # Validate token
        user_id = await validate_mobile_token(access_token)
        
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM notifications 
            WHERE JSON_EXTRACT(recipients, '$') LIKE ? OR recipients IS NULL
            ORDER BY created_at DESC 
            LIMIT ?
        """, (f"%{user_id}%", limit))
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                "id": row[0],
                "case_id": row[1],
                "notification_type": row[2],
                "message": row[3],
                "priority": row[4],
                "created_at": row[5],
                "read_at": row[6],
                "status": row[7]
            })
        
        conn.close()
        
        return {
            "status": "success",
            "notifications": notifications,
            "total": len(notifications),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get mobile notifications error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get mobile notifications error: {str(e)}")

@router.post("/notifications/register")
async def register_mobile_notifications(access_token: str, device_token: str, platform: str = "ios"):
    """Register device for push notifications"""
    try:
        # Validate token
        user_id = await validate_mobile_token(access_token)
        
        # Store device token
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mobile_device_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                device_token TEXT,
                platform TEXT,
                created_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        cursor.execute("""
            INSERT OR REPLACE INTO mobile_device_tokens 
            (user_id, device_token, platform, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, device_token, platform, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "Device registered for notifications",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Register mobile notifications error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Register mobile notifications error: {str(e)}")

@router.post("/sync")
async def mobile_sync(request: MobileSyncRequest, access_token: str):
    """Mobile app data synchronization"""
    try:
        # Validate token
        user_id = await validate_mobile_token(access_token)
        
        last_sync = datetime.fromisoformat(request.last_sync.replace('Z', '+00:00'))
        
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        # Get updated cases
        cursor.execute("""
            SELECT * FROM workflow_cases 
            WHERE updated_at > ?
            ORDER BY updated_at DESC
        """, (last_sync.isoformat(),))
        
        updated_cases = []
        for row in cursor.fetchall():
            updated_cases.append({
                "case_id": row[0],
                "patient_id": row[1],
                "purpose": row[2],
                "icd_code": row[3],
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6],
                "metadata": json.loads(row[7]) if row[7] else {}
            })
        
        # Get new notifications
        cursor.execute("""
            SELECT * FROM notifications 
            WHERE created_at > ? AND JSON_EXTRACT(recipients, '$') LIKE ?
            ORDER BY created_at DESC
        """, (last_sync.isoformat(), f"%{user_id}%"))
        
        new_notifications = []
        for row in cursor.fetchall():
            new_notifications.append({
                "id": row[0],
                "case_id": row[1],
                "notification_type": row[2],
                "message": row[3],
                "priority": row[4],
                "created_at": row[5],
                "read_at": row[6],
                "status": row[7]
            })
        
        conn.close()
        
        return {
            "status": "success",
            "sync_data": {
                "updated_cases": updated_cases,
                "new_notifications": new_notifications,
                "sync_timestamp": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Mobile sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Mobile sync error: {str(e)}")

@router.get("/dashboard")
async def get_mobile_dashboard(access_token: str):
    """Get mobile dashboard data"""
    try:
        # Validate token
        user_id = await validate_mobile_token(access_token)
        
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        # Get dashboard metrics
        cursor.execute("SELECT COUNT(*) FROM workflow_cases")
        total_cases = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM workflow_cases WHERE status IN ('created', 'processing', 'queued')")
        active_cases = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM workflow_cases WHERE status = 'completed'")
        completed_cases = cursor.fetchone()[0]
        
        # Get unread notifications count
        cursor.execute("""
            SELECT COUNT(*) FROM notifications 
            WHERE read_at IS NULL AND JSON_EXTRACT(recipients, '$') LIKE ?
        """, (f"%{user_id}%",))
        unread_notifications = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "success",
            "dashboard": {
                "total_cases": total_cases,
                "active_cases": active_cases,
                "completed_cases": completed_cases,
                "unread_notifications": unread_notifications,
                "user_id": user_id
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get mobile dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get mobile dashboard error: {str(e)}")

async def validate_mobile_token(access_token: str) -> str:
    """Validate mobile access token and return user_id"""
    try:
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id FROM mobile_sessions 
            WHERE access_token = ? AND is_active = 1 AND expires_at > ?
        """, (access_token, datetime.now().timestamp()))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return row[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Token validation error")

@router.get("/health")
async def mobile_api_health():
    """Mobile API health check"""
    return {
        "status": "healthy",
        "service": "mobile_api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
