# Day 7-8 Queue and Reliability Notes

## Day 7 flow

1. Order Service validates the user through User Service.
2. Order Service commits the order.
3. Order Service calls Notification Service with `X-Internal-API-Key` and `order-confirmation:{order_id}` as the idempotency key.
4. Notification Service persists the job and returns `202 Accepted` after Celery accepts it.
5. The worker processes the job asynchronously and updates its state.

The delivery adapter currently logs a processed notification. It does not deliver real email/SMS. The Operations deployment worker currently changes registry version metadata; it does not invoke an AWS deployment API.

## Day 8 behavior

- `/health` is liveness only; it should not require databases or Redis.
- `/ready` checks dependencies required by that process. A dependency outage returns `503` with component-level state.
- Order-to-Notification calls have a short timeout, bounded exponential retry, and an in-process circuit breaker. When notification enqueue remains unavailable, order creation succeeds and logs that the notification was not queued. This is graceful degradation, not a durable cross-service outbox guarantee.
- Celery tasks use late acknowledgments, retry backoff, and job state persistence. The worker uses `solo` locally on Windows; Linux deployments can use the normal worker pool.
- FastAPI lifespans dispose async DB engines and close Redis clients during shutdown.

## Local failure exercises

Run services with their configured local `.env` values. Start Redis and PostgreSQL, then run each API and worker using the service README/commands.

| Experiment | Injected failure | Expected observation | Recovery |
| --- | --- | --- | --- |
| User Service down | Stop User API, keep Order online | Order `/ready` returns `503`; order creation fails user validation with `503`; no order is committed | Restart User API; `/ready` recovers |
| Notification API down | Stop Notification API | Order tries bounded requests, then completes order creation, logs notification enqueue failure; circuit opens after repeated failed order requests | Restart Notification API; after breaker cooldown one probe is allowed and successful enqueue closes it |
| Redis down | Stop Redis | Notification/Operations `/ready` returns `503`; enqueue/deployment may be recorded as `FAILED` if broker dispatch fails | Restart Redis and Celery workers; retry with same idempotency key to requeue failed work |
| Worker down | Stop a Celery worker but leave Redis/API online | Queue API can accept jobs; Notification `/ready` or Operations `/ready` reports worker unavailable; job stays queued | Restart worker; queued task runs and its persisted state advances |
| PostgreSQL down | Stop the service database | Relevant `/ready` returns `503`; writes fail rather than claiming success | Restore DB; restart if connection pool does not recover; readiness returns `200` |

For each exercise record timestamp, injected failure, endpoint/status, job state, recovery action, and recovery latency. A real external delivery provider and an outbox are required before promising guaranteed notification delivery after an Order API process crash.
