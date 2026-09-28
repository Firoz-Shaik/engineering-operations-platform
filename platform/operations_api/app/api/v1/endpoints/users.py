from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser
from app.clients.user_service_client import user_service_client


router = APIRouter()


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(current_user: CurrentUser):
    user = await user_service_client.get_user(current_user.id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user