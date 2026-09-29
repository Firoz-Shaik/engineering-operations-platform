# Operations API: health and deployment jobs

## Deployment jobs

`POST /api/v1/deployments/` creates a durable idempotent deployment job and responds with `202 Accepted`. `GET /api/v1/deployments/{id}` reads its state. Jobs progress through `QUEUED`, `RUNNING`, then `SUCCESS` or `FAILED`; transient worker errors are retried with exponential backoff.

The current executor is intentionally a local demonstration: on success it updates the service registry's `version`. It does not create or update AWS infrastructure. Replace this adapter with an AWS deployment provider before using the endpoint for real deployments.

Run the API and worker from this directory after configuring `.env` and applying Alembic migrations:

```powershell
python -m alembic upgrade head
uvicorn main:app --reload --port 8001
celery -A app.tasks.celery_app.celery_app worker --pool=solo --loglevel=INFO
```

`GET /health` reports process liveness. `GET /ready` checks PostgreSQL (`SELECT 1`), Redis (`PING`), and worker responsiveness. The existing authenticated `/api/v1/services/health` routes perform live probes against registered service URLs; these remain on-demand checks rather than a scheduled monitoring system.