from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from src.database import SessionLocal
from src.models import User, UserRole
from .auth import get_current_user

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- Schemas -----

class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str]
    role: UserRole
    is_active: bool

    class Config:
        orm_mode = True

class UserProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, description="Updated full name of the user")
    # Optionally allow updates to more fields in future

# ----- Endpoints -----

# PUBLIC_INTERFACE
@router.get(
    "/me",
    summary="Get own user profile",
    description="Get the current authenticated user's profile information.",
    response_model=UserProfileResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get the profile of the current authenticated user.
    """
    return current_user

# PUBLIC_INTERFACE
@router.put(
    "/me",
    summary="Update own user profile",
    description="Update basic profile fields (e.g., full_name) for the current authenticated user.",
    response_model=UserProfileResponse,
)
def update_my_profile(
    req: UserProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the profile (e.g. full_name) of the currently authenticated user.
    Raises 400 if no updatable fields are provided.
    """
    data = req.dict(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update.")
    for field, value in data.items():
        setattr(current_user, field, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

# PUBLIC_INTERFACE
@router.put(
    "",
    summary="Update current user's profile (root PUT)",
    description="Allows updating profile using /profile (PUT) as well.",
    response_model=UserProfileResponse,
)
def put_profile_root(
    req: UserProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Alternate PUT /profile endpoint for frontend compatibility."""
    return update_my_profile(req, db, current_user)
