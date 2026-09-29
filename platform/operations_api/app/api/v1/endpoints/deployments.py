from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import AdminUser, DBSession
from app.schemas.deployment import DeploymentCreate, DeploymentRead
from app.services.deployment_service import deployment_service
from fastapi import HTTPException


router = APIRouter()


@router.post("/", response_model=DeploymentRead, status_code=status.HTTP_202_ACCEPTED)
async def create_deployment(
    db: DBSession,
    deployment: DeploymentCreate,
    current_user: AdminUser,
):
    return await deployment_service.create_deployment(db, data=deployment)


@router.get("/{deployment_id}", response_model=DeploymentRead)
async def get_deployment(
    db: DBSession,
    deployment_id: UUID,
    current_user: AdminUser,
):
    deployment = await deployment_service.get_deployment(
        db, deployment_id=deployment_id
    )
    if deployment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")
    return deployment