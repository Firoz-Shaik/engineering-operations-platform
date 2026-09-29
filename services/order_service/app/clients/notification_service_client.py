import asyncio
import logging
from uuid import UUID

import httpx

from app.core.config import settings
from app.clients.user_service_client import UserServiceUser
from app.clients.circuit_breaker import AsyncCircuitBreaker


logger = logging.getLogger(__name__)


class NotificationServiceClient:
    def __init__(self) -> None:
        self._breaker = AsyncCircuitBreaker(failure_threshold=5, reset_timeout=15.0)

    async def enqueue_order_confirmation(
        self, *, order_id: UUID, user: UserServiceUser
    ) -> bool:
        if not await self._breaker.allow_request():
            logger.warning("notification circuit is open; skipping order %s enqueue", order_id)
            return False

        url = (
            f"{settings.NOTIFICATION_SERVICE_URL.rstrip('/')}/api/v1/notifications/"
            "order-confirmation"
        )
        body = {
            "idempotency_key": f"order-confirmation:{order_id}",
            "recipient": str(user.email),
            "order_id": str(order_id),
            "payload": {"full_name": user.full_name},
        }
        headers = {"X-Internal-API-Key": settings.INTERNAL_API_KEY}

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    response = await client.post(url, json=body, headers=headers)
                if response.status_code < 500:
                    response.raise_for_status()
                    await self._breaker.record_success()
                    return True
                if response.status_code not in {502, 503, 504}:
                    response.raise_for_status()
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                if attempt == 2:
                    logger.warning(
                        "notification enqueue failed for order %s: %s", order_id, exc
                    )
                    await self._breaker.record_failure()
                    return False
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "notification service rejected order %s enqueue: %s",
                    order_id,
                    exc.response.status_code,
                )
                await self._breaker.record_failure()
                return False

            if attempt < 2:
                await asyncio.sleep(0.1 * (2**attempt))

        logger.warning("notification enqueue exhausted retries for order %s", order_id)
        await self._breaker.record_failure()
        return False


notification_service_client = NotificationServiceClient()