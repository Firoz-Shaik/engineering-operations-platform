# Indexing and Caching Strategy

## Scope and assumptions

This strategy covers User Service, Order Service, and Operations API as currently implemented. There are no measured production request rates yet, and Redis is not currently configured or used by these services. The index choices below follow actual query predicates and sort order; validate them against realistic data with PostgreSQL query plans before treating them as permanent capacity decisions.

Redis caching is a proposed next step, not active application behavior. Do not report an endpoint as cached until Redis connectivity, fallback behavior, invalidation, and tests have been implemented.

## Database indexes added

| Service/table | Index or constraint | Query served |
| --- | --- | --- |
| User `users` | Unique `email` | Credential lookup, duplicate prevention, and user lookup by email |
| User `roles` | Unique `name` | Role lookup by normalized name and duplicate prevention |
| User `user_roles` | Unique `(user_id, role_id)` | Prevent duplicate assignments; supports checks scoped to one user |
| User `user_roles` | `(role_id, user_id)` | Role-filtered user listing and reverse lookup by role |
| User `users` | Partial `(created_at, id)` where `deleted_at IS NULL` | Active-user list ordering and stable pagination |
| Order `orders` | `(created_at, id)` | Unfiltered order listing and deterministic pagination |
| Order `orders` | `(status, created_at, id)` | Status-filtered order listing and deterministic pagination |
| Order `orders` | `(user_id, created_at, id)` | Orders-by-user lookup and stable ordering |
| Order `order_items` | `(order_id)` | Select-in loading of items and efficient parent deletion cascade |
| Operations `services` | `(environment_id)` | Environment-scoped service listing and efficient environment cascade |

Primary-key indexes already cover UUID lookups. No index was added for `services.status`: the current API does not filter or order by status. No environment-name index was added because no current query looks environments up by name.

Each service owns its own Alembic migration. Before deploying these revisions to any database, run the migration check in that service. User uniqueness was checked against the current development database; each target environment must still be checked before migration. If duplicates exist in a target, clean them up deliberately before applying unique constraints.

## Endpoint cache policy

| Endpoint/data | Recommendation | TTL | Invalidation |
| --- | --- | --- | --- |
| User `GET /roles/` | Cache role catalog; small and infrequently changed | 5 minutes | Delete role-list key after role creation; clear on role rename/delete if added later |
| User `GET /users/{id}` and internal lookup | Do not cache initially; internal lookup participates in order creation and user deletion/role state can change | None initially | A later short TTL cache needs invalidation on user update, soft delete, role assignment/removal, and should not be used as the sole authorization source |
| User `GET /users/by-email/{email}` and login lookup | Do not cache initially; credential and active-user state are security sensitive | None | Never cache password verification or tokens |
| User `GET /users/` | Do not cache initially; role, pagination, user mutations, and soft delete make invalidation broad | None | Revisit after measuring hit rate and list volume |
| Order `GET /orders/{id}` | Candidate only after load data; current order writes are mutable | 15-30 seconds if measured worthwhile | Invalidate on update/delete; populate/invalidate on create |
| Order `GET /orders/` and `/orders/users/{user_id}` | Do not cache initially; pagination and frequent order writes create many keys and invalidation fanout | None | Revisit with request metrics; key must include status, page, authenticated user scope, and filters |
| Operations `GET /environments/` | Cache catalog | 5 minutes | Invalidate after environment creation/update/delete |
| Operations `GET /services/` and `/services/{id}` | Cache only after service changes and health-status writes reliably invalidate all affected keys | 15-30 seconds | Invalidate on service create/update/delete and after every probe that writes status |
| Operations `GET /services/health` and `/{id}/health` | Never cache a live probe response as a fresh result | None | Each request probes the registered URL. If a future UI needs polling, return a clearly timestamped last-known sample from a separate monitoring store |
| Operations `GET /users/me` | Do not cache initially; user record is owned by User Service and may change | None | A later proxy cache must be user-ID scoped and have a short TTL |
| Health endpoints (`/health`) | Do not cache | None | Health checks should represent current process/service availability |

## Redis implementation requirements

When activating Redis:

1. Configure `REDIS_URL` per deployment environment and provide a managed Redis endpoint in AWS; never hardcode credentials in source.
2. Use a key namespace including application and environment, for example `eop:prod:user:roles:v1` and `eop:staging:ops:environments:v1`. Do not let staging and production share a namespace.
3. Cache JSON response DTOs, not ORM objects or database sessions.
4. Use TTLs as an upper bound on staleness and explicit invalidation after successful database commits.
5. Make Redis unavailable a cache miss: API correctness must continue from PostgreSQL, and cache failures must not fail requests.
6. Never allow a cache hit to bypass JWT verification, ownership checks, RBAC checks, or User Service validation.
7. Add cache hit/miss/error metrics and tests for invalidation before enabling caches in production.

## Validation and tuning

For each index, compare representative queries before and after migration using `EXPLAIN (ANALYZE, BUFFERS)`. Test small and production-like row counts: PostgreSQL may correctly choose a sequential scan on a small table. Track index size and write latency as data grows. Remove indexes that have low usage or duplicate a more selective index.

Before adding broader caches, record endpoint request rates, p50/p95 latency, database query counts, mutation rates, and acceptable staleness for each response. Cache only when those measurements show a material benefit.
