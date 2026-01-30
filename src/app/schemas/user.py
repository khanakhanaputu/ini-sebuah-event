import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models.user import PlatformRole, UserStatus # Pastikan import Enum ini ada
from app.models.user import UserStatus # Pastikan import ini

# ==========================================
# 1. SCHEMA REQUEST (INPUT DARI USER)
# ==========================================
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(
        default=None, 
        min_length=3, 
        max_length=100,
        description="Nama lengkap sesuai KTP"
    )
    
    phone_number: str = Field(
        ..., 
        description="Nomor HP aktif (WA). Contoh: 081234567890"
    )

    @field_validator('phone_number')
    @classmethod
    def validate_and_format_phone(cls, v: str) -> str:
        if not v:
            raise ValueError("Nomor HP tidak boleh kosong")

        # 1. Sanitize
        cleaned = re.sub(r'[\s\-\(\)\.]', '', v)

        # 2. Cek angka
        if not re.match(r'^\+?\d+$', cleaned):
            raise ValueError('Nomor HP hanya boleh berisi angka')

        # 3. Normalisasi (08 -> 628)
        if cleaned.startswith('0'):
            cleaned = '62' + cleaned[1:]
        elif cleaned.startswith('+62'):
            cleaned = cleaned[1:]

        # 4. Validasi Panjang
        if not (10 <= len(cleaned) <= 15):
            raise ValueError('Panjang nomor HP tidak valid (harus 10-15 digit)')

        return cleaned

    @field_validator('full_name')
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Nama terlalu pendek')

        if not re.match(r"^[a-zA-Z\s\.\']+$", v):
            raise ValueError("Nama hanya boleh berisi huruf, spasi, titik, dan tanda petik")

        return v.title()

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Budi Santoso",
                "phone_number": "081234567890"
            }
        }


# ==========================================
# 2. SCHEMA RESPONSE (OUTPUT KE FRONTEND)
# ==========================================
# Inilah yang tadi hilang! 👇
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar: Optional[str] = None
    role: PlatformRole # Atau str kalau mau simpel
    user_status: UserStatus # Atau str kalau mau simpel

    # PENTING: Config ini wajib biar Pydantic bisa baca data dari SQLAlchemy
    model_config = ConfigDict(from_attributes=True)



# --- NEW: SCHEMA UPDATE STATUS ---
class UserStatusUpdate(BaseModel):
    user_status: UserStatus # Dropdown: active, suspended, banned



class UserPublicResponse(BaseModel):
    """Public user info (untuk search results)"""
    id: int
    name: str
    email: str
    picture: str | None = None
    
    class Config:
        from_attributes = True