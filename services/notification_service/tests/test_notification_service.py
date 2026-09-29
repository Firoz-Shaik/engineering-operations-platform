import os
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/notifications")
os.environ.setdefault("INTERNAL_API_KEY", "test-internal-key")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/2")

from app.schemas.notification import OrderNotificationCreate
from app.services import notification_service as service_module


class FakeSession:
    def __init__(self):
        self.commits = 0

    async def commit(self):
        self.commits += 1


@pytest.mark.asyncio
async def test_enqueue_returns_accepted_and_dispatches_once(monkeypatch):
    job = SimpleNamespace(id=uuid4(), state="queued", last_error=None)
    repository = Mock()
    repository.create_or_get_order_notification = Mock()

    async def create_or_get(_db, *, data):
        return job, True

    repository.create_or_get_order_notification = create_or_get
    enqueue = Mock()
    monkeypatch.setattr(service_module, "notification_repository", repository)
    monkeypatch.setattr(service_module.process_notification, "apply_async", enqueue)

    request = OrderNotificationCreate(
        idempotency_key="order-confirmation:abc",
        recipient="customer@example.com",
        order_id=uuid4(),
    )
    result = await service_module.notification_service.enqueue_order_confirmation(
        FakeSession(), data=request
    )

    assert result.id == job.id
    assert result.state == "queued"
    assert result.duplicate is False
    enqueue.assert_called_once()


@pytest.mark.asyncio
async def test_duplicate_job_is_not_dispatched_again(monkeypatch):
    job = SimpleNamespace(id=uuid4(), state="success", last_error=None)

    async def create_or_get(_db, *, data):
        return job, False

    repository = SimpleNamespace(
        create_or_get_order_notification=create_or_get
    )
    enqueue = Mock()
    monkeypatch.setattr(service_module, "notification_repository", repository)
    monkeypatch.setattr(service_module.process_notification, "apply_async", enqueue)

    request = OrderNotificationCreate(
        idempotency_key="order-confirmation:abc",
        recipient="customer@example.com",
        order_id=uuid4(),
    )
    result = await service_module.notification_service.enqueue_order_confirmation(
        FakeSession(), data=request
    )

    assert result.duplicate is True
    assert result.state == "success"
    enqueue.assert_not_called()


@pytest.mark.asyncio
async def test_queue_failure_marks_job_failed_and_returns_503(monkeypatch):
    job = SimpleNamespace(id=uuid4(), state="queued", last_error=None)

    async def create_or_get(_db, *, data):
        return job, True

    repository = SimpleNamespace(
        create_or_get_order_notification=create_or_get
    )
    enqueue = Mock(side_effect=ConnectionError("broker down"))
    monkeypatch.setattr(service_module, "notification_repository", repository)
    monkeypatch.setattr(service_module.process_notification, "apply_async", enqueue)
    db = FakeSession()

    request = OrderNotificationCreate(
        idempotency_key="order-confirmation:abc",
        recipient="customer@example.com",
        order_id=uuid4(),
    )
    with pytest.raises(HTTPException) as raised:
        await service_module.notification_service.enqueue_order_confirmation(
            db, data=request
        )

    assert raised.value.status_code == 503
    assert job.state == "failed"
    assert db.commits == 1
