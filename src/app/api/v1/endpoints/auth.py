# src/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, or_
from app.deps.db import get_db
from app.core.security import verify_password, maybe_upgrade_hash, create_access_token, md5_hex,create_verify_email_token, decode_verify_email_token
from typing import Any, Dict
from datetime import datetime, timedelta
import secrets
from app.core.security import create_bsha256  # <— gunakan hash aman untuk user baru
from app.schemas.auth import RegistrationIn, MessageOnly, TokenOut, LoginIn, GoogleAuthIn
from app.models.user import User, PlatformRole, UserStatus
from app.core.email import send_verify_email

# keperluan google
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.config import settings



router = APIRouter()

async def _read_form_or_json(req: Request) -> Dict[str, Any]:
    ctype = (req.headers.get("content-type") or "").lower()
    if "application/x-www-form-urlencoded" in ctype or "multipart/form-data" in ctype:
        form = await req.form()
        return {k: (form.get(k) if form.get(k) is not None else "") for k in form.keys()}
    try:
        body = await req.json()
        return {k: (body.get(k) if body.get(k) is not None else "") for k in body.keys()}
    except Exception:
        return {}
    
async def _read_credentials(req: Request) -> tuple[str, str]:
    ctype = (req.headers.get("content-type") or "").lower()
    if "application/x-www-form-urlencoded" in ctype or "multipart/form-data" in ctype:
        form = await req.form()
        return (str(form.get("username") or ""), str(form.get("password") or ""))
    data = await req.json()
    return (str(data.get("username") or ""), str(data.get("password") or ""))


async def _issue_legacy_token(db: AsyncSession, user_id: int) -> str:
    """
    Coba pakai tabel access_tokens seperti sistem lama.
    Jika tabel tidak ada / gagal insert, fallback ke JWT.
    """
    tok = secrets.token_hex(32)
    try:
        exp = datetime.utcnow() + timedelta(days=30)
        await db.execute(
            text("""INSERT INTO access_tokens (id, user_id, revoked, created_at, expires_at)
                    VALUES (:id, :uid, 0, NOW(), :exp)"""),
            {"id": tok, "uid": user_id, "exp": exp},
        )
        await db.commit()
        return tok
    except Exception:
        # fallback: JWT
        return create_access_token(str(user_id))


@router.post("/login")
async def login(
    request: Request,
    payload: LoginIn,
    db: AsyncSession = Depends(get_db),
) -> Any:
    # --- ambil kredensial ---
    identity, password = await _read_credentials(request)
    if not identity or not password:
        raise HTTPException(
            status_code=422,
            detail="username & password required"
        )

    # --- ambil user ---
    res = await db.execute(
        select(User).where(or_(
            User.username == identity,
            User.email == identity,
        ))
    )
    user: User | None = res.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Username atau Password salah"
        )

    # cek apakah login pake gogole apa engga
    if user.auth_provider == "google":
        raise HTTPException(
            400,
            "Akun ini login menggunakan Google"
        )

    # --- verifikasi password (legacy compatible) ---
    valid = (
        verify_password(password, user.password_hash)
        or md5_hex(password) == user.password_hash
    )

    if not valid:
        raise HTTPException(
            status_code=401,
            detail="Username atau Password salah"
        )

    # --- upgrade hash jika perlu ---
    new_hash = maybe_upgrade_hash(password, user.password_hash)
    if new_hash:
        user.password_hash = new_hash
        await db.commit()

    # --- issue token (PAKAI JWT MODERN) ---
    access_token = create_access_token(
        sub=str(user.id),
        extra={
            "role": user.platform_role.value
            if hasattr(user.platform_role, "value")
            else user.platform_role
        }
    )

    # --- response ---
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "platform_role": user.platform_role,
            "email_verified": user.email_verified_at is not None,
        }
    }

# ...imports lain di file ini tetap
from app.core.security import create_bsha256  # <— gunakan hash aman untuk user baru

@router.post(
    "/registrasi",
    response_model=TokenOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrasi + Auto Login"
)
async def registrasi(
    request: Request,
    payload: RegistrationIn | None = Body(default=None),
    db: AsyncSession = Depends(get_db),
):
    if payload is None:
        raw = await _read_form_or_json(request)
        payload = RegistrationIn(**raw)

    # cek email
    q = await db.execute(
        select(User).where(User.email == payload.email)
    )
    if q.scalar_one_or_none():
        raise HTTPException(400, "Email telah terdaftar")

    # cek username
    q = await db.execute(
        select(User).where(User.username == payload.username)
    )
    if q.scalar_one_or_none():
        raise HTTPException(400, "Username telah digunakan")

    try:
        user = User(
            username=payload.username,
            email=payload.email,
            phone=payload.phone,
            password_hash=create_bsha256(payload.password),
            platform_role=PlatformRole.USER,
            status=UserStatus.ACTIVE,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)  # ⬅️ WAJIB

        access_token = create_access_token(
            sub=str(user.id),
            extra={
                "role": user.platform_role.value
            }
        )

        # # send verifikasi email
        # verify_token_email = create_verify_email_token(user.id)
        # link_verify_email = f"http://localhost:8000/auth/verify-email?token={verify_token_email}"
        # await send_verify_email(user.email, link_verify_email)


        # return json
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "platform_role": user.platform_role,
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
        
@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_verify_email_token(token)
    user_id = payload["sub"]

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(400, "User tidak ditemukan")

    if user.email_verified_at:
        return {"message": "Email sudah diverifikasi"}

    user.email_verified_at = datetime.utcnow()
    await db.commit()

    return {"message": "Email berhasil diverifikasi"}


# register pakai google
@router.post("/google")
async def auth_google(
    payload: GoogleAuthIn,
    db: AsyncSession = Depends(get_db)
):

    # tanpa google (dev mode)
    if not settings.GOOGLE_CLIENT_ID:
        if not payload.email:
            raise HTTPException(
                400, 
                "DEV MODE: email wajib dikirim"
            )
        
        email = payload.email
        username = payload.username or email.split("@")[0]
        google_sub = f"dev-google-{email}"

    # prod mode: kalau udah ada GOOGLE_CLIENT_ID
    else:
        try:
            info = id_token.verify_oauth2_token(
                payload.id_token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        except Exception as e:
            raise HTTPException(
                401,
                f"Google token tidak valid: {str(e)}"
            )
        
        email = info["email"]
        google_sub = info["sub"]
        username = info.get("name", "")
    
    # logic 
    res = await db.execute(
        select(User).where(User.email == email)
    )

    user = res.scalar_one_or_none()

    try:
        if not user:
            user = User(
                username=username,
                email=email,
                platform_role=PlatformRole.USER,
                status=UserStatus.ACTIVE,
                email_verified_at=datetime.utcnow(),
                google_id=google_sub,
                auth_provider='google'
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

        access_token = create_access_token(
            sub=str(user.id),
            extra={
                "role": user.platform_role.value
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "platform_role": user.platform_role,  
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )