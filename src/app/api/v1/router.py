from fastapi import APIRouter
from .endpoints import auth, users, organizers, organizer_members

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/user", tags=["user"])
api_router.include_router(organizers.router, prefix="/organizers", tags=["Organizers"])
api_router.include_router(organizer_members.router, prefix="/organizers", tags=["Organizer Members"])