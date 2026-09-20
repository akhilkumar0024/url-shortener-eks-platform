# Analytics Backend (`analytics-backend`)

A read-only analytics service built with FastAPI, PostgreSQL, and Alembic migrations.

---

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/clicks` | Returns paginated list of recent click events (`short_code`, `clicked_at`, `referrer`, `user_agent`, `client_ip`). Accepts `limit` (default 50) and `offset` (default 0). |
| `GET`  | `/stats`  | Returns aggregated statistics: click counts grouped by `short_code`, and click counts grouped chronologically by hourly time buckets. |
| `GET`  | `/healthz`| Container health probe endpoint. |

---

## 2. Database Schema Ownership

`analytics-backend` exclusively owns the schema for the `analytics` table via Alembic migrations.
It uses a dedicated version table `alembic_version_analytics` to isolate its migrations from `api-service`.

### Table Schema: `analytics`
- `id` (INTEGER, Primary Key, autoincrement)
- `short_code` (VARCHAR, Indexed, NOT NULL)
- `clicked_at` (TIMESTAMP WITH TIME ZONE, Indexed, DEFAULT NOW())
- `referrer` (TEXT, NULL)
- `user_agent` (TEXT, NULL)
- `client_ip` (TEXT, NULL)
- `metadata` (JSONB, DEFAULT `'{}'::jsonb`)

To apply migrations:
```bash
alembic upgrade head
```

To seed local test data after running migrations:
```bash
python seed.py
```

---

## 3. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/shortener` | PostgreSQL database connection string. |
| `CORS_ORIGINS` | `*` | Comma-separated list of allowed CORS origins (e.g. `http://localhost:3000`). |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
