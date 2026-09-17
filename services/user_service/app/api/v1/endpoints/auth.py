from app.services.auth_service import auth_service
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.token import Token
from app.api.deps import DBSession

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: DBSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return await auth_service.auth_user_for_token(
        db, email=form_data.username, password=form_data.password
    )