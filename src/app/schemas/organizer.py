from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.models.organizer import OrganizerStatus
import re


class OrganizerBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    

class OrganizerCreate(OrganizerBase):
    pass

    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9\s\-_.]+$', v):
            raise ValueError('Nama organizer hanya boleh berisi huruf, angka, spasi, dan karakter - _ .')
        return v.strip()


class OrganizerUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=100)
    status: OrganizerStatus | None = None


class OrganizerResponse(OrganizerBase):
    id: int
    slug: str
    status: OrganizerStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrganizerWithMembersResponse(OrganizerResponse):
    member_count: int | None = None
    user_role: str | None = None  # Role user yang sedang login di organizer ini