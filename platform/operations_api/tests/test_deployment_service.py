import os
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/operations")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/3")

from app.schemas.deployment import DeploymentCreate
from app.services import deployment_service as service_module


class FakeSession:
    pass


@pytest.mark.asyncio
async def test_new_deployment_is_queued_once(monkeypatch):
    service_id = uuid4()
    deployment = SimpleNamespace(
        id=uuid4(),
        service_id=service_id,
        target_version="2.0.0",
        idempotency_key="deploy-2.0.0",
        state="QUEUED",
        attempts=0,
        error=None,
        execution_mode="registry_version_update",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    async def get_service(_db, *, service_id):
        return object()

    async def create_or_get(_db, *, data):
        return deployment, True

    monkeypatch.setattr(
        service_module.operations_repository, "get_service_by_id", get_service
    )
    monkeypatch.setattr(
        service_module.deployment_repository, "create_or_get", create_or_get
    )
    enqueue = Mock()
    monkeypatch.setattr(service_module.execute_deployment, "apply_async", enqueue)

    request = DeploymentCreate(
        service_id=service_id,
        target_version="2.0.0",
        idempotency_key="deploy-2.0.0",
    )
    accepted = await service_module.deployment_service.create_deployment(
        FakeSession(), data=request
    )

    assert accepted.id == deployment.id
    assert accepted.state == "QUEUED"
    enqueue.assert_called_once_with(args=[str(deployment.id)], task_id=str(deployment.id))


@pytest.mark.asyncio
async def test_unknown_service_rejected_before_job_creation(monkeypatch):
    async def missing_service(_db, *, service_id):
        return None

    monkeypatch.setattr(
        service_module.operations_repository,
        "get_service_by_id",
        missing_service,
    )
    create_or_get = Mock()
    monkeypatch.setattr(
        service_module.deployment_repository, "create_or_get", create_or_get
    )
    request = DeploymentCreate(
        service_id=uuid4(),
        target_version="2.0.0",
        idempotency_key="missing-service",
    )

    with pytest.raises(HTTPException) as raised:
        await service_module.deployment_service.create_deployment(
            FakeSession(), data=request
        )

    assert raised.value.status_code == 404
    create_or_get.assert_not_called()
