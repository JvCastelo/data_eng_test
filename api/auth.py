import hashlib
from typing import Optional

from db import SessionLocal
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.data import ApiKey, User
from sqlalchemy.orm import Session

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_api_key(api_key: str, db: Session) -> Optional[ApiKey]:

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    db_api_key = (
        db.query(ApiKey)
        .filter(ApiKey.hashed_key == key_hash, ApiKey.is_active == True)
        .first()
    )

    if db_api_key:
        db_api_key.user = db.query(User).filter(User.id == db_api_key.user_id).first()

    return db_api_key


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):

    api_key = credentials.credentials
    db_api_key = verify_api_key(api_key, db)

    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida ou inativa",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "api_key": api_key,
        "api_key_id": db_api_key.id,
        "user_id": db_api_key.user_id,
        "username": db_api_key.user.username,
        "authenticated": True,
    }
