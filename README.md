# CloudScale URL Shortener Platform (Monorepo)

A production-grade, distributed URL shortener system designed for high throughput, low latency, and operational observability.

---

## 1. Repository Structure

```
url-shortener/
├── api-service/          # FastAPI: URL shortening, Base62 encoding, Redis caching, 302 redirects, SQS publishing, Prometheus metrics
├── analytics-backend/    # FastAPI: Read-only telemetry API for paginated click logs and aggregated statistics
├── analytics-frontend/   # React (Vite + Recharts + Nginx): Sleek real-time observability telemetry dashboard
├── lambda-worker/        # Hand-written AWS Lambda worker (documented schema contract)
├── infra/                # Hand-written Terraform & Kubernetes manifests
├── scripts/              # Seed scripts for development
└── docker-compose.yml    # Full local development stack with automated Alembic migrations
```

---

## 2. Architecture & Design Principles

- **Zero Clutter**: Intentionally minimal business logic without authentication, rate-limiting, or admin UI overhead — optimized for infrastructure showcase (Kubernetes/EKS, AWS SQS, Redis, RDS/Postgres, Prometheus).
- **Decoupled Database Migrations**: `api-service` exclusively owns the `urls` table, while `analytics-backend` exclusively owns the `analytics` table. Both run independent Alembic migration revisions using isolated version tables (`alembic_version_api` and `alembic_version_analytics`) to prevent collisions in the shared PostgreSQL database.
- **Sub-Millisecond Read Latency**: Short link redirects check Redis first. On cache miss, the target URL is fetched from PostgreSQL and cached with a 1-hour TTL.
- **Asynchronous Telemetry Ingestion**: Click analytics are dispatched to AWS SQS via non-blocking background tasks without delaying the HTTP 302 redirect response.
- **Structured JSON Logging**: All services emit single-line structured JSON logs with contextual metadata.
- **Prometheus Observability**: Request volume and latency histograms are exposed via `/metrics`.

---

## 3. Quick Start (Local Development)

### Prerequisites
- Docker Engine & Docker Compose

### Start the Stack
Start PostgreSQL, Redis, run database migrations, and launch all services:

```bash
docker compose up --build -d
```

### Check Container Status
```bash
docker compose ps
```

### Seed Test Data (Optional)
To populate the `analytics` table with realistic test data for the dashboard:
```bash
docker compose exec analytics-backend python /app/seed.py
```

### Access Services
- **Telemetry Dashboard**: [http://localhost:3000](http://localhost:3000)
- **API Service**: [http://localhost:8000](http://localhost:8000)
  - Interactive OpenAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Health Probe: [http://localhost:8000/healthz](http://localhost:8000/healthz)
  - Prometheus Metrics: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- **Analytics Backend**: [http://localhost:8001](http://localhost:8001)
  - Interactive OpenAPI Docs: [http://localhost:8001/docs](http://localhost:8001/docs)
  - Recent Clicks: [http://localhost:8001/clicks](http://localhost:8001/clicks)
  - Statistics: [http://localhost:8001/stats](http://localhost:8001/stats)
