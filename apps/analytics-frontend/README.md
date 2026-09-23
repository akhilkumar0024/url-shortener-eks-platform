# Analytics Frontend (`analytics-frontend`)

A modern telemetry dashboard built with React 18, Vite, and Recharts, served via Nginx.

---

## 1. Features

- **Summary Metric Cards**: Real-time KPI summaries for total click volume, active short codes, and top link performance.
- **Categorical Visualization**: Interactive Recharts Bar Chart detailing click counts grouped by `short_code`.
- **Temporal Trends**: Interactive Recharts Area Chart displaying hourly click volume velocity over time.
- **Recent Click Events Table**: Detailed, responsive event log with UTC timestamps, client IPs, referrers, and user-agent details, including pagination.
- **Link Generator Sandbox**: Interactive UI tool to create a short link on `api-service` and test redirects immediately.

---

## 2. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8001` | Base URL of `analytics-backend` for `/clicks` and `/stats`. |
| `VITE_SHORTENER_API_URL` | `http://localhost:8000` | Base URL of `api-service` for creating test links. |

---

## 3. Docker Production Deployment

The provided Dockerfile uses a multi-stage build:
1. Builds optimized static bundle via `node:20-alpine`.
2. Serves static assets via lightweight `nginx:alpine`.

```bash
docker build -t analytics-frontend .
docker run -p 3000:80 analytics-frontend
```
