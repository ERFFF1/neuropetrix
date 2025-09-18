from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import secrets
import hashlib

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None

# Mock user database
USERS_DB = {
    "admin": User(
        id="admin_001",
        username="admin",
        email="admin@neuropetrix.com",
        full_name="System Administrator",
        role="admin",
        is_active=True,
        created_at=datetime.now()
    ),
    "doctor": User(
        id="doc_001",
        username="doctor",
        email="doctor@neuropetrix.com",
        full_name="Dr. Medical Expert",
        role="doctor",
        is_active=True,
        created_at=datetime.now()
    ),
    "radiologist": User(
        id="rad_001",
        username="radiologist",
        email="radiologist@neuropetrix.com",
        full_name="Dr. Radiologist",
        role="radiologist",
        is_active=True,
        created_at=datetime.now()
    )
}

# Password hashes (in real app, store in database)
PASSWORD_HASHES = {
    "admin": pwd_context.hash("admin123"),
    "doctor": pwd_context.hash("doctor123"),
    "radiologist": pwd_context.hash("radiologist123")
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    user = USERS_DB.get(username)
    if not user:
        return None
    if not user.is_active:
        return None
    
    hashed_password = PASSWORD_HASHES.get(username)
    if not hashed_password or not verify_password(password, hashed_password):
        return None
    
    # Update last login
    user.last_login = datetime.now()
    return user

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """Verify and decode a token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        token_type_check: str = payload.get("type")
        
        if username is None or token_type_check != token_type:
            return None
            
        return TokenData(username=username, user_id=user_id, role=role)
    except JWTError:
        return None

def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username."""
    return USERS_DB.get(username)

def check_permissions(user_role: str, required_roles: list) -> bool:
    """Check if user has required permissions."""
    role_hierarchy = {
        "admin": ["admin", "doctor", "radiologist", "user"],
        "doctor": ["doctor", "radiologist", "user"],
        "radiologist": ["radiologist", "user"],
        "user": ["user"]
    }
    
    allowed_roles = role_hierarchy.get(user_role, [])
    return any(role in allowed_roles for role in required_roles)

def generate_api_key(user_id: str) -> str:
    """Generate an API key for a user."""
    timestamp = str(int(datetime.now().timestamp()))
    data = f"{user_id}:{timestamp}:{SECRET_KEY}"
    api_key = hashlib.sha256(data.encode()).hexdigest()
    return f"np_{api_key[:32]}"

def verify_api_key(api_key: str) -> Optional[str]:
    """Verify an API key and return user_id."""
    if not api_key.startswith("np_"):
        return None
    
    # In real app, check against database
    # For now, return mock user_id
    return "admin_001"

# Session management
class SessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, user: User, token: str) -> str:
        """Create a new session."""
        session_id = secrets.token_urlsafe(32)
        self.active_sessions[session_id] = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "token": token,
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        session = self.active_sessions.get(session_id)
        if session:
            session["last_activity"] = datetime.now()
        return session
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            if now - session_data["last_activity"] > timedelta(hours=24):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]

# Global session manager
session_manager = SessionManager()

# Health check function for auth
def auth_health_check():
    """Auth service health check."""
    return {
        "status": "healthy",
        "service": "Authentication Service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "active_users": len(USERS_DB),
        "active_sessions": len(session_manager.active_sessions)
    }
