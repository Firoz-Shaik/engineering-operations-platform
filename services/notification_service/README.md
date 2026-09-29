# Notification Service

This service accepts internal order-confirmation requests, persists idempotent notification jobs, and queues them to a Celery worker using Redis. The development delivery adapter logs that a job was processed; it does not send email or SMS. A provider adapter must be configured before treating `SUCCESS` as actual delivery.

## Configuration

Copy `.env.example` to `.env`, configure `DATABASE_URL`, `REDIS_URL`, and a strong `INTERNAL_API_KEY` shared with Order Service. Apply the service-owned schema:

```powershell
python -m alembic upgrade head
```

## Run API and worker

Run both from this service directory:

```powershell
uvicorn main:app --reload --port 8004
celery -A app.tasks.celery_app.celery_app worker --pool=solo --loglevel=INFO
```

Use Celery's default process pool on supported Linux deployments; `--pool=solo` is suitable for local Windows development.

## Endpoints

- `GET /health`: process liveness; no database or broker calls.
- `GET /ready`: requires database, Redis broker, and a responding Celery worker.
- `POST /api/v1/notifications/order-confirmation`: internal API-key protected; returns `202` after durable job creation and queue acceptance.
- `GET /api/v1/notifications/{job_id}`: internal API-key protected job state.

Supported job states: `queued`, `running`, `retrying`, `success`, `failed`. The idempotency key prevents duplicate jobs for an order confirmation. Failed enqueue jobs can be retried with the same key.