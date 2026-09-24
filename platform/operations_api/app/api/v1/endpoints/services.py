from uuid import UUID
from fastapi import APIRouter, status, HTTPException
from app.core.database import DBSession
from app.services.operations_service import operations_service
from app.services.environments_service import environments_service
from app.schemas.service import Service, ServiceCreate

router = APIRouter()

@router.get("/", response_model=list[Service], status_code=status.HTTP_200_OK)
async def get_services(db: DBSession):
    return await operations_service.get_all_services(db)

@router.get("/{service_id}", response_model=Service, status_code=status.HTTP_200_OK)
async def get_service_by_id(db: DBSession, service_id: UUID):
    service = await operations_service.get_service_by_id(db, service_id=service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service

@router.post("/", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(db: DBSession, service: ServiceCreate):
    env = await environments_service.get_environment_by_id(
        db=db, environment_id=service.environment_id
    )
    if not env:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")
    return await operations_service.create_service(db, obj_in=service)

    