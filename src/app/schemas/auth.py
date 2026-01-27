from pydantic import BaseModel, EmailStr, Field
from datetime import date

class LoginIn(BaseModel):
    identity: str  # bisa email/username
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    platform_role: str | None = None



class RegistrationIn(BaseModel):
    username: str = Field(min_length=3, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=6, max_length=20)
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

class MessageOnly(BaseModel):
    message: str

class GoogleAuthIn(BaseModel):
    id_token: str | None = None  # optional for dev
    email: EmailStr | None = None
    username: str | None = None