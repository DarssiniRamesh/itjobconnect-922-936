from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from .auth import get_current_user
from src.models import User

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

# ----- Schemas -----

class NotificationResponse(BaseModel):
    id: int
    message: str
    is_read: bool

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
@router.get(
    "/",
    summary="List notifications for current user",
    description="Returns a list of notifications for the currently authenticated user.",
    response_model=List[NotificationResponse]
)
def list_notifications(current_user: User = Depends(get_current_user)):
    """
    Placeholder: List notifications for the current user.
    Returns an empty list; real logic would query a Notification table.
    """
    # In the future, would query Notification table.
    return []
