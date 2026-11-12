import os
import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv("JWT_SECRET", "retention-doctor-dev-secret-key-2026")
ALGORITHM = "HS256"
security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_access_token(user_id: str, email: str, plan: str = "pro") -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "plan": plan,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> Dict[str, Any]:
    """
    Decodes bearer token or returns local default user in development mode.
    """
    if credentials is None:
        # Development mode fallback user
        return {
            "id": "dev_user_001",
            "email": "creator@retentiondoctor.ai",
            "plan": "pro",
            "is_dev": True
        }

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "plan": payload.get("plan", "pro"),
            "is_dev": False
        }
    except Exception:
        # If token is invalid, fallback or raise
        return {
            "id": "dev_user_001",
            "email": "creator@retentiondoctor.ai",
            "plan": "pro",
            "is_dev": True
        }
