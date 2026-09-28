import asyncio
from datetime import datetime, timezone
from uuid import UUID
from urllib.parse import urlsplit

import httpx
from fastapi import HTTPException, status
from app.models.service import Service
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.operations_repository import operations_repository
from app.schemas.service import ServiceCreate, ServiceHealth, ServiceUpdate

class OperationsService:

    async def get_all_services(self, db: AsyncSession) -> list[Service]:
        result = await operations_repository.get_all_services(db)
        if not result:
            return []
        return result

    async def get_service_by_id(self, db: AsyncSession, *, service_id: UUID) -> Service | None:
        return await operations_repository.get_service_by_id(db, service_id=service_id)
    async def create_service(self, db: AsyncSession, *, obj_in: ServiceCreate) -> Service:
        return await operations_repository.create_service(db, obj_in=obj_in)

    async def update_service(
        self, db: AsyncSession, *, service_id: UUID, obj_in: ServiceUpdate
    ) -> Service | None:
        return await operations_repository.update_service(
            db, service_id=service_id, obj_in=obj_in
        )

    async def delete_service(self, db: AsyncSession, *, service_id: UUID) -> bool:
        return await operations_repository.delete_service(db, service_id=service_id)

    async def check_service_health(
        self, db: AsyncSession, *, service_id: UUID
    ) -> ServiceHealth | None:
        service = await operations_repository.get_service_by_id(db, service_id=service_id)
        if service is None:
            return None
        result = await self._probe_service(service)
        await operations_repository.update_service_status(
            db,
            service_id=service.id,
            service_status="healthy" if result.is_healthy else "unhealthy",
        )
        return result

    async def check_all_services_health(self, db: AsyncSession) -> list[ServiceHealth]:
        services = await operations_repository.get_all_services(db)
        results = await asyncio.gather(*(self._probe_service(service) for service in services))
        for result in results:
            await operations_repository.update_service_status(
                db,
                service_id=result.service_id,
                service_status="healthy" if result.is_healthy else "unhealthy",
            )
        return results

    @staticmethod
    async def _probe_service(service: Service) -> ServiceHealth:
        base_url = service.base_url.rstrip("/")
        health_path = service.health_enpoint.strip()
        url = f"{base_url}/{health_path.lstrip('/')}"
        started_at = asyncio.get_running_loop().time()
        checked_at = datetime.now(timezone.utc)
        parsed_base_url = urlsplit(base_url)
        if parsed_base_url.scheme not in {"http", "https"} or not parsed_base_url.hostname:
            return ServiceHealth(
                service_id=service.id,
                name=service.name,
                url=url,
                is_healthy=False,
                response_time_ms=0,
                checked_at=checked_at,
                error="Registered base URL must be an absolute HTTP(S) URL",
            )
        try:
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=False) as client:
                response = await client.get(url)
            response_time_ms = (asyncio.get_running_loop().time() - started_at) * 1000
            return ServiceHealth(
                service_id=service.id,
                name=service.name,
                url=url,
                is_healthy=200 <= response.status_code < 300,
                http_status=response.status_code,
                response_time_ms=round(response_time_ms, 2),
                checked_at=checked_at,
                error=None if 200 <= response.status_code < 300 else "Health endpoint returned a non-2xx status",
            )
        except httpx.TimeoutException:
            return ServiceHealth(
                service_id=service.id,
                name=service.name,
                url=url,
                is_healthy=False,
                response_time_ms=round((asyncio.get_running_loop().time() - started_at) * 1000, 2),
                checked_at=checked_at,
                error="Health check timed out",
            )
        except httpx.RequestError:
            return ServiceHealth(
                service_id=service.id,
                name=service.name,
                url=url,
                is_healthy=False,
                response_time_ms=round((asyncio.get_running_loop().time() - started_at) * 1000, 2),
                checked_at=checked_at,
                error="Health endpoint is unreachable",
            )

operations_service = OperationsService()