from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
import hashlib
from string import hexdigits
import bcrypt
from app.core.config import settings

ALGO = "HS256"
BCRYPT_ROUNDS = 12
PREFIX = "bsha256$"   # skema baru: bcrypt( sha256(password) )

def md5_hex(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def sha256_bytes(s: str) -> bytes:
    return hashlib.sha256(s.encode("utf-8")).digest()

def _is_md5_hex(h: str) -> bool:
    return len(h) == 32 and all(c in hexdigits for c in h.lower())

def _is_legacy_bcrypt(h: str) -> bool:
    return h.startswith("$2a$") or h.startswith("$2b$") or h.startswith("$2y$")

def _is_bsha256(h: str) -> bool:
    return h.startswith(PREFIX)

def _bcrypt_hash_bytes(b: bytes) -> str:
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(b, salt).decode("utf-8")

def create_bsha256(raw: str) -> str:
    return PREFIX + _bcrypt_hash_bytes(sha256_bytes(raw))

def verify_password(raw: str, stored: str) -> bool:
    # 1) skema baru: bcrypt(sha256(password)) — aman >72 byte
    if _is_bsha256(stored):
        hashed = stored[len(PREFIX):].encode("utf-8")
        return bcrypt.checkpw(sha256_bytes(raw), hashed)

    # 2) hash bcrypt lama — truncate ke 72 byte supaya aman
    if _is_legacy_bcrypt(stored):
        return bcrypt.checkpw(raw.encode("utf-8")[:72], stored.encode("utf-8"))

    # 3) hash MD5 lama
    if _is_md5_hex(stored):
        return md5_hex(raw) == stored

    return False

def maybe_upgrade_hash(raw: str, stored: str) -> str | None:
    # Upgrade legacy bcrypt/MD5 ke skema baru
    if _is_bsha256(stored):
        return None
    if _is_legacy_bcrypt(stored) or _is_md5_hex(stored):
        return create_bsha256(raw)
    return None

def create_access_token(sub: str, extra: dict | None = None) -> str:
    data = {"sub": sub,
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
    if extra:
        data.update(extra)
    return jwt.encode(data, settings.SECRET_KEY, algorithm=ALGO)

def create_verify_email_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256"
    )
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGO]
        )
        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token sudah kedaluwarsa"
        )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token tidak valid"
        )

def decode_verify_email_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGO]
        )
        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=400,
            detail="Link verifikasi sudah kedaluwarsa"
        )

    except JWTError:
        raise HTTPException(
            status_code=400,
            detail="Token verifikasi tidak valid"
        )