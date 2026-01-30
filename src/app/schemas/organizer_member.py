from pydantic import BaseModel
from datetime import datetime
from app.models.organizer_member import Role, Status


class OrganizerMemberBase(BaseModel):
    role: Role


class OrganizerMemberInvite(OrganizerMemberBase):
    user_id: int


class OrganizerMemberUpdate(BaseModel):
    role: Role | None = None
    status: Status | None = None


class OrganizerMemberResponse(OrganizerMemberBase):
    organizer_id: int
    user_id: int
    status: Status
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrganizerMemberWithUserResponse(OrganizerMemberResponse):
    user_name: str | None = None
    user_email: str | None = None

class OrganizerMemberInviteByEmail(BaseModel):
    email: str
    role: Role