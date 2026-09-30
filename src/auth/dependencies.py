from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Dict, Any
from src.auth.security import decode_access_token
from src.db.nosql_manager import get_nosql_db, BaseNoSQLDatabase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: BaseNoSQLDatabase = Depends(get_nosql_db)
) -> Dict[str, Any]:
    """FastAPI dependency to extract and authenticate current user from Bearer token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
        
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    user = db.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
        
    # Remove sensitive password hash from returned user object
    user_safe = dict(user)
    user_safe.pop("hashed_password", None)
    return user_safe

async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: BaseNoSQLDatabase = Depends(get_nosql_db)
) -> Optional[Dict[str, Any]]:
    """Optional user authentication dependency for guest / anonymous fallbacks"""
    if not token:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
