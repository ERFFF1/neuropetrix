from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
# import jwt  # Mock implementation
import hashlib
import secrets
import sqlite3
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/security", tags=["Security & Authentication"])

# JWT Configuration
SECRET_KEY = "neuropetrix_secret_key_2025_ultra_secure"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()

class UserLogin(BaseModel):
    username: str
    password: str
    device_info: Optional[Dict[str, Any]] = None

class UserRegister(BaseModel):
    username: str
    password: str
    email: str
    full_name: str
    role: str
    department: str
    permissions: List[str] = []

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class UserProfile(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: str
    role: str
    department: str
    permissions: List[str]
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: UserProfile

# Mock user database (in production, use proper database)
USERS_DB = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "user_id": "admin_001",
        "email": "admin@neuropetrix.com",
        "full_name": "System Administrator",
        "role": "admin",
        "department": "IT",
        "permissions": ["*"],  # All permissions
        "created_at": "2025-01-01T00:00:00",
        "is_active": True
    },
    "doctor": {
        "password_hash": hashlib.sha256("doctor123".encode()).hexdigest(),
        "user_id": "doctor_001",
        "email": "doctor@hospital.com",
        "full_name": "Dr. John Smith",
        "role": "radiologist",
        "department": "Radiology",
        "permissions": ["read_cases", "create_cases", "approve_reports", "view_analytics"],
        "created_at": "2025-01-01T00:00:00",
        "is_active": True
    },
    "nurse": {
        "password_hash": hashlib.sha256("nurse123".encode()).hexdigest(),
        "user_id": "nurse_001",
        "email": "nurse@hospital.com",
        "full_name": "Nurse Jane Doe",
        "role": "nurse",
        "department": "Oncology",
        "permissions": ["read_cases", "update_patient_info"],
        "created_at": "2025-01-01T00:00:00",
        "is_active": True
    }
}

# Active sessions
ACTIVE_SESSIONS = {}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token (mock implementation)"""
    # Mock JWT token generation
    token_data = {
        "sub": data.get("sub"),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access"
    }
    # Return a mock token
    return f"mock_access_token_{secrets.token_urlsafe(32)}"

def create_refresh_token(data: dict):
    """Create JWT refresh token (mock implementation)"""
    # Mock refresh token generation
    return f"mock_refresh_token_{secrets.token_urlsafe(32)}"

def verify_token(token: str) -> dict:
    """Verify JWT token (mock implementation)"""
    # Mock token verification
    if token.startswith("mock_access_token_"):
        return {"sub": "admin", "type": "access"}
    elif token.startswith("mock_refresh_token_"):
        return {"sub": "admin", "type": "refresh"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    username = payload.get("sub")
    if username is None or username not in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = USERS_DB[username]
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    return user

def check_permission(user: dict, required_permission: str) -> bool:
    """Check if user has required permission"""
    if "*" in user["permissions"]:  # Admin has all permissions
        return True
    return required_permission in user["permissions"]

@router.post("/login", response_model=TokenResponse)
async def login(user_login: UserLogin):
    """User login endpoint"""
    try:
        # Validate user
        if user_login.username not in USERS_DB:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        user = USERS_DB[user_login.username]
        password_hash = hashlib.sha256(user_login.password.encode()).hexdigest()
        
        if user["password_hash"] != password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )
        
        # Create tokens
        access_token = create_access_token(data={"sub": user_login.username})
        refresh_token = create_refresh_token(data={"sub": user_login.username})
        
        # Store session
        session_id = secrets.token_urlsafe(32)
        ACTIVE_SESSIONS[session_id] = {
            "user_id": user["user_id"],
            "username": user_login.username,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "created_at": datetime.now().isoformat(),
            "device_info": user_login.device_info
        }
        
        # Update last login
        user["last_login"] = datetime.now().isoformat()
        
        # Create user profile
        user_profile = UserProfile(
            user_id=user["user_id"],
            username=user_login.username,
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            department=user["department"],
            permissions=user["permissions"],
            created_at=user["created_at"],
            last_login=user["last_login"],
            is_active=user["is_active"]
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_info=user_profile
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        payload = verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        username = payload.get("sub")
        if username not in USERS_DB:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        user = USERS_DB[username]
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )
        
        # Create new access token
        new_access_token = create_access_token(data={"sub": username})
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """User logout endpoint"""
    try:
        # Remove user sessions
        sessions_to_remove = []
        for session_id, session in ACTIVE_SESSIONS.items():
            if session["user_id"] == current_user["user_id"]:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del ACTIVE_SESSIONS[session_id]
        
        return {
            "status": "success",
            "message": "Logged out successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        user_id=current_user["user_id"],
        username=current_user.get("username", ""),
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        department=current_user["department"],
        permissions=current_user["permissions"],
        created_at=current_user["created_at"],
        last_login=current_user.get("last_login"),
        is_active=current_user["is_active"]
    )

@router.put("/profile")
async def update_user_profile(
    profile_update: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        # Update allowed fields
        allowed_fields = ["email", "full_name", "department"]
        for field, value in profile_update.items():
            if field in allowed_fields:
                current_user[field] = value
        
        return {
            "status": "success",
            "message": "Profile updated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    try:
        # Verify current password
        current_password_hash = hashlib.sha256(password_change.current_password.encode()).hexdigest()
        if current_user["password_hash"] != current_password_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        new_password_hash = hashlib.sha256(password_change.new_password.encode()).hexdigest()
        current_user["password_hash"] = new_password_hash
        
        # Invalidate all sessions for this user
        sessions_to_remove = []
        for session_id, session in ACTIVE_SESSIONS.items():
            if session["user_id"] == current_user["user_id"]:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del ACTIVE_SESSIONS[session_id]
        
        return {
            "status": "success",
            "message": "Password changed successfully. Please login again.",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.get("/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if not check_permission(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    users = []
    for username, user in USERS_DB.items():
        users.append({
            "username": username,
            "user_id": user["user_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "department": user["department"],
            "is_active": user["is_active"],
            "created_at": user["created_at"],
            "last_login": user.get("last_login")
        })
    
    return {
        "status": "success",
        "users": users,
        "total": len(users),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/users")
async def create_user(
    user_data: UserRegister,
    current_user: dict = Depends(get_current_user)
):
    """Create new user (admin only)"""
    if not check_permission(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    if user_data.username in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create new user
    password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()
    user_id = f"user_{len(USERS_DB) + 1:03d}"
    
    USERS_DB[user_data.username] = {
        "password_hash": password_hash,
        "user_id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "department": user_data.department,
        "permissions": user_data.permissions,
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    
    return {
        "status": "success",
        "message": "User created successfully",
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/sessions")
async def get_active_sessions(current_user: dict = Depends(get_current_user)):
    """Get active sessions for current user"""
    user_sessions = []
    for session_id, session in ACTIVE_SESSIONS.items():
        if session["user_id"] == current_user["user_id"]:
            user_sessions.append({
                "session_id": session_id,
                "created_at": session["created_at"],
                "device_info": session.get("device_info", {})
            })
    
    return {
        "status": "success",
        "sessions": user_sessions,
        "total": len(user_sessions),
        "timestamp": datetime.now().isoformat()
    }

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Revoke specific session"""
    if session_id in ACTIVE_SESSIONS:
        session = ACTIVE_SESSIONS[session_id]
        if session["user_id"] == current_user["user_id"]:
            del ACTIVE_SESSIONS[session_id]
            return {
                "status": "success",
                "message": "Session revoked successfully",
                "timestamp": datetime.now().isoformat()
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Session not found"
    )

@router.get("/permissions")
async def get_user_permissions(current_user: dict = Depends(get_current_user)):
    """Get current user permissions"""
    return {
        "status": "success",
        "permissions": current_user["permissions"],
        "role": current_user["role"],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def security_health():
    """Security service health check"""
    return {
        "status": "healthy",
        "service": "security",
        "version": "1.0.0",
        "active_sessions": len(ACTIVE_SESSIONS),
        "total_users": len(USERS_DB),
        "timestamp": datetime.now().isoformat()
    }
