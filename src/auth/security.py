from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
import hashlib
from src.config import Config

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed bcrypt password"""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        # Fallback verification
        salt = hashed_password[:16] if len(hashed_password) > 32 else ""
        computed = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
        return hashed_password.endswith(computed)

def get_password_hash(password: str) -> str:
    """Generate bcrypt hash for password"""
    try:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    except Exception:
        import secrets
        salt = secrets.token_hex(8)
        hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        return f"{salt}${hashed}"

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT access token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
