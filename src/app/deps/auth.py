from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User, UserStatus
from app.deps.db import get_db
from app.core.security import decode_access_token
from app.models.user import PlatformRole

security = HTTPBearer()

credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Kredensial tidak valid atau token kadaluarsa",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token_auth: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    token = token_auth.credentials
    payload = decode_access_token(token)
    
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credential_exception
    
    user = await db.get(User, int(user_id))
    if not user:
        raise credential_exception
    
    if user.user_status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Akun Anda sedang dalam status: {user.user_status.value}"
        )
    
    return user

async def get_current_active_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Cek apakah user yang login adalah PLATFORM_ADMIN.
    Kalau bukan, tolak (403 Forbidden).
    """
    if current_user.role != PlatformRole.PLATFORM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki akses Super Admin."
        )
    return current_user