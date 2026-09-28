from uuid import UUID
from fastapi import APIRouter, Response, status, HTTPException
from app.core.database import DBSession
from app.services.operations_service import operations_service
from app.services.environments_service import environments_service
from app.schemas.service import Service, ServiceCreate, ServiceHealth, ServiceUpdate
from app.api.deps import AdminUser

router = APIRouter()

@router.get("/", response_model=list[Service], status_code=status.HTTP_200_OK)
async def get_services(db: DBSession, current_user: AdminUser):
    return await operations_service.get_all_services(db)


@router.get("/health", response_model=list[ServiceHealth], status_code=status.HTTP_200_OK)
async def check_all_services_health(db: DBSession, current_user: AdminUser):
    return await operations_service.check_all_services_health(db)


@router.get("/{service_id}/health", response_model=ServiceHealth, status_code=status.HTTP_200_OK)
async def check_service_health(
    db: DBSession,
    service_id: UUID,
    current_user: AdminUser,
):
    result = await operations_service.check_service_health(db, service_id=service_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return result


@router.get("/{service_id}", response_model=Service, status_code=status.HTTP_200_OK)
async def get_service_by_id(db: DBSession, service_id: UUID, current_user: AdminUser):
    service = await operations_service.get_service_by_id(db, service_id=service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service

@router.post("/", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(db: DBSession, service: ServiceCreate, current_user: AdminUser):
    env = await environments_service.get_environment_by_id(
        db=db, environment_id=service.environment_id
    )
    if not env:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")
    return await operations_service.create_service(db, obj_in=service)


@router.patch("/{service_id}", response_model=Service, status_code=status.HTTP_200_OK)
async def update_service(
    db: DBSession,
    service_id: UUID,
    service: ServiceUpdate,
    current_user: AdminUser,
):
    updated_service = await operations_service.update_service(
        db, service_id=service_id, obj_in=service
    )
    if updated_service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return updated_service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    db: DBSession,
    service_id: UUID,
    current_user: AdminUser,
):
    deleted = await operations_service.delete_service(db, service_id=service_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

    