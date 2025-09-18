from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import timedelta, datetime
from backend.core.auth import (
    authenticate_user, create_access_token, create_refresh_token,
    verify_token, get_user_by_username, check_permissions,
    generate_api_key, verify_api_key, session_manager,
    UserCreate, UserLogin, Token, TokenData, User, USERS_DB
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_username(token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Dependency to check permissions
def require_permissions(required_roles: list):
    """Dependency factory for role-based access control."""
    def permission_checker(current_user: User = Depends(get_current_user)):
        if not check_permissions(current_user.role, required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return permission_checker

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Authenticate user and return tokens."""
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )
    
    # Create session
    session_id = session_manager.create_session(user, access_token)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800  # 30 minutes
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    token_data = verify_token(refresh_token, "refresh")
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = get_user_by_username(token_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,  # Keep the same refresh token
        expires_in=1800
    )

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user and invalidate session."""
    # In real app, add token to blacklist
    return {"message": "Successfully logged out"}

@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate, admin_user: User = Depends(require_permissions(["admin"]))):
    """Register a new user (admin only)."""
    # Check if username already exists
    if get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user (in real app, save to database)
    new_user = User(
        id=f"user_{len(USERS_DB) + 1}",
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True,
        created_at=datetime.now()
    )
    
    # Store password hash
    from backend.core.auth import get_password_hash, PASSWORD_HASHES
    PASSWORD_HASHES[user_data.username] = get_password_hash(user_data.password)
    
    # Add to users database
    from backend.core.auth import USERS_DB
    USERS_DB[user_data.username] = new_user
    
    return new_user

@router.get("/users", response_model=list[User])
async def list_users(admin_user: User = Depends(require_permissions(["admin"]))):
    """List all users (admin only)."""
    return list(USERS_DB.values())

@router.post("/api-key")
async def generate_user_api_key(current_user: User = Depends(get_current_user)):
    """Generate API key for current user."""
    api_key = generate_api_key(current_user.id)
    return {
        "api_key": api_key,
        "user_id": current_user.id,
        "created_at": datetime.now().isoformat()
    }

@router.post("/verify-api-key")
async def verify_user_api_key(api_key: str):
    """Verify API key and return user info."""
    user_id = verify_api_key(api_key)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Find user by ID
    user = None
    for u in USERS_DB.values():
        if u.id == user_id:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return {"user": user, "api_key_valid": True}

@router.get("/sessions")
async def get_active_sessions(admin_user: User = Depends(require_permissions(["admin"]))):
    """Get all active sessions (admin only)."""
    return {
        "active_sessions": len(session_manager.active_sessions),
        "sessions": list(session_manager.active_sessions.keys())
    }

@router.delete("/sessions/{session_id}")
async def invalidate_session(session_id: str, admin_user: User = Depends(require_permissions(["admin"]))):
    """Invalidate a specific session (admin only)."""
    success = session_manager.invalidate_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {"message": "Session invalidated successfully"}

@router.get("/permissions")
async def get_user_permissions(current_user: User = Depends(get_current_user)):
    """Get current user's permissions."""
    role_permissions = {
        "admin": ["read", "write", "delete", "admin"],
        "doctor": ["read", "write"],
        "radiologist": ["read", "write"],
        "user": ["read"]
    }
    
    return {
        "user": current_user.username,
        "role": current_user.role,
        "permissions": role_permissions.get(current_user.role, [])
    }

@router.get("/health")
async def auth_health():
    """Auth service health check."""
    from backend.core.auth import auth_health_check
    return auth_health_check()
