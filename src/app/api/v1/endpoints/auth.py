from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any

# --- Dependencies & Config ---
from app.deps.db import get_db
from app.core.config import settings
from app.core.security import create_access_token

# --- Schemas ---
# Pastikan di app/schemas/auth.py cuma butuh GoogleAuthIn & TokenOut
from app.schemas.auth import GoogleAuthIn, TokenOut

# --- Models ---
from app.models.user import User, PlatformRole, UserStatus

# --- Google Auth Lib ---
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

router = APIRouter()

# ==========================================
# SINGLE GATE: GOOGLE LOGIN / REGISTER
# ==========================================
@router.post(
    "/google", 
    response_model=TokenOut, 
    status_code=status.HTTP_200_OK
)
async def auth_google(
    payload: GoogleAuthIn,
    db: AsyncSession = Depends(get_db)
):
    """
    Satu-satunya pintu masuk user.
    Menerima ID Token dari Google.
    - Jika email belum ada di DB -> Auto Register.
    - Jika email sudah ada -> Login & Generate Token.
    """
    
    email = ""
    google_sub = ""
    username = ""
    avatar = None

    # ---------------------------------------------------------
    # 1. VERIFIKASI TOKEN GOOGLE
    # ---------------------------------------------------------
    
    # A. Mode Development (Bypass Verify jika GOOGLE_CLIENT_ID belum diset)
    if not settings.GOOGLE_CLIENT_ID:
        if not payload.email:
            raise HTTPException(400, "DEV MODE: Email wajib dikirim di body (mocking)")
        
        # Data Mocking
        email = payload.email
        username = payload.username or email.split("@")[0]
        google_sub = f"dev-google-{email}" # Fake Google ID
        avatar = "https://ui-avatars.com/api/?name=" + username

    # B. Mode Production (Wajib Verify ke Server Google)
    else:
        try:
            # Library Google akan validasi signature tokennya
            id_info = id_token.verify_oauth2_token(
                payload.id_token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            # Ambil data user dari token Google
            email = id_info["email"]
            google_sub = id_info["sub"] # ID Unik dari Google
            username = id_info.get("name", email.split("@")[0])
            avatar = id_info.get("picture")
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail=f"Token Google Invalid: {str(e)}"
            )

    # ---------------------------------------------------------
    # 2. CEK USER DI DATABASE
    # ---------------------------------------------------------
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        # --- SKENARIO: USER LAMA (LOGIN) ---
        
        # Cek status takutnya user kena Banned
        if user.user_status != UserStatus.ACTIVE:
            raise HTTPException(403, "Akun anda telah dinonaktifkan.")
        
        # (Opsional) Update data user biar sinkron sama Google terbaru
        # user.full_name = username 
        # user.avatar = avatar
        # await db.commit()
        
    else:
        # --- SKENARIO: USER BARU (AUTO REGISTER) ---
        user = User(
            email=email,
            full_name=username,
            google_id=google_sub,
            avatar=avatar,
            role=PlatformRole.USER,       # Default jadi User biasa
            user_status=UserStatus.ACTIVE # Default langsung aktif
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user) # Refresh buat dapet ID baru

    # ---------------------------------------------------------
    # 3. GENERATE TOKEN APLIKASI (JWT)
    # ---------------------------------------------------------
    # Ini token yang dipakai frontend buat request API selanjutnya
    access_token = create_access_token(
        sub=str(user.id),
        extra={"role": user.role.value}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name, # Pakai full_name karena di modelmu full_name
        "platform_role": user.role
    }