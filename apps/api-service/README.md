# API Service (`api-service`)

A high-performance URL shortening and redirection service built with FastAPI, Redis caching, SQLAlchemy, PostgreSQL, and AWS SQS event publishing.

---

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/shorten` | Accepts `{ "url": "<long_url>" }`. Inserts row, base62-encodes database sequence `id`, persists `short_code`, and returns `{ "short_url": "https://mymegham.cloud/<short_code>" }`. |
| `GET`  | `/{short_code}` | Checks Redis first (key: `short_code`). On miss, queries Postgres and populates Redis with 1-hour TTL. Issues HTTP 302 redirect. Asynchronously publishes click event to SQS via background task without blocking redirect. |
| `GET`  | `/healthz` | Kubernetes liveness and readiness probe endpoint (returns `{"status": "ok"}`). |
| `GET`  | `/metrics` | Exposes Prometheus metrics (request counts, latency histograms via `prometheus-fastapi-instrumentator`). |

---

## 2. SQS Message JSON Contract

When a user visits a shortened URL, `api-service` extracts HTTP request metadata and publishes the following JSON payload to an AWS SQS queue via FastAPI's `BackgroundTasks`:

```json
{
  "short_code": "4e",
  "timestamp": "2026-09-17T07:15:00.123456+00:00",
  "referrer": "https://news.ycombinator.com",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "client_ip": "203.0.113.195",
  "metadata": {}
}
```

### Fields:
- `short_code` (*string, required*): The short code that was requested.
- `timestamp` (*string, ISO 8601 UTC, required*): Timestamp when the redirect occurred.
- `referrer` (*string or null*): Value of the incoming HTTP `Referer` header.
- `user_agent` (*string or null*): Value of the incoming HTTP `User-Agent` header.
- `client_ip` (*string or null*): Client IP extracted from `X-Forwarded-For` or the socket.
- `metadata` (*object*): Extensible JSON metadata dictionary.

---

## 3. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/shortener` | PostgreSQL connection string. |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL. |
| `REDIS_TTL_SECONDS` | `3600` | TTL in seconds for cached URLs in Redis (1 hour). |
| `SQS_QUEUE_URL` | `""` | AWS SQS Queue URL for click analytics events. |
| `AWS_REGION` | `us-east-1` | AWS region for SQS client. |
| `MOCK_SQS` | `true` | When `true`, logs the SQS JSON payload using structured JSON and skips AWS API calls (ideal for local dev). |
| `BASE_URL` | `https://mymegham.cloud` | Domain prefix used to format the returned `short_url`. |
| `LOG_LEVEL` | `INFO` | Logging level. |

---

## 4. Database Migrations (Alembic)

`api-service` exclusively owns the schema for the `urls` table. It uses a dedicated version table `alembic_version_api` to ensure no collisions occur when sharing a PostgreSQL database with other services.

To apply migrations:
```bash
alembic upgrade head
```
