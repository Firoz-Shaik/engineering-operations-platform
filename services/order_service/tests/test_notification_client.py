import httpx
import pytest
from uuid import uuid4

from app.clients import notification_service_client as client_module
from app.clients.circuit_breaker import AsyncCircuitBreaker
from app.clients.user_service_client import UserServiceUser


class FakeAsyncClient:
    responses: list[httpx.Response] = []
    requests: list[tuple[str, dict, dict]] = []

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def post(self, url, *, json, headers):
        self.requests.append((url, json, headers))
        return self.responses.pop(0)


def response(status_code: int) -> httpx.Response:
    return httpx.Response(status_code, request=httpx.Request("POST", "http://test"))


@pytest.mark.asyncio
async def test_notification_client_retries_transient_server_errors(monkeypatch):
    user = UserServiceUser(
        id=uuid4(), email="person@example.com", full_name="Test User", roles=[]
    )
    order_id = uuid4()
    FakeAsyncClient.responses = [response(503), response(502), response(202)]
    FakeAsyncClient.requests = []
    monkeypatch.setattr(client_module.httpx, "AsyncClient", FakeAsyncClient)
    async def no_wait(_seconds):
        return None
    monkeypatch.setattr(client_module.asyncio, "sleep", no_wait)

    queued = await client_module.notification_service_client.enqueue_order_confirmation(
        order_id=order_id, user=user
    )

    assert queued is True
    assert len(FakeAsyncClient.requests) == 3
    sent_url, payload, headers = FakeAsyncClient.requests[-1]
    assert sent_url.endswith("/api/v1/notifications/order-confirmation")
    assert payload["idempotency_key"] == f"order-confirmation:{order_id}"
    assert payload["recipient"] == "person@example.com"
    assert headers["X-Internal-API-Key"]


@pytest.mark.asyncio
async def test_notification_client_gracefully_returns_false_after_retries(monkeypatch):
    user = UserServiceUser(
        id=uuid4(), email="person@example.com", full_name="Test User", roles=[]
    )
    FakeAsyncClient.responses = [response(503), response(503), response(503)]
    FakeAsyncClient.requests = []
    monkeypatch.setattr(client_module.httpx, "AsyncClient", FakeAsyncClient)
    async def no_wait(_seconds):
        return None
    monkeypatch.setattr(client_module.asyncio, "sleep", no_wait)

    queued = await client_module.notification_service_client.enqueue_order_confirmation(
        order_id=uuid4(), user=user
    )

    assert queued is False
    assert len(FakeAsyncClient.requests) == 3


@pytest.mark.asyncio
async def test_circuit_breaker_allows_only_one_half_open_probe():
    breaker = AsyncCircuitBreaker(failure_threshold=2, reset_timeout=0)

    assert await breaker.allow_request() is True
    await breaker.record_failure()
    assert await breaker.allow_request() is True
    await breaker.record_failure()
    assert breaker.state == "open"

    assert await breaker.allow_request() is True
    assert await breaker.allow_request() is False
    await breaker.record_success()
    assert breaker.state == "closed"
