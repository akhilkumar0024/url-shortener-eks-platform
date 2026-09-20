# Lambda Worker Specification & Database Contract

> **Note**: This worker is hand-written separately. This document defines the exact database schema, SQL statement, and SQS event contract required for implementation.

---

## 1. Database Table Contract

The worker connects to PostgreSQL using `psycopg2` (or `psycopg`) and inserts click events into the `analytics` table.

### Schema Definition (`analytics` table)

| Column Name   | PostgreSQL Type            | Constraints / Defaults | Description |
|---------------|----------------------------|------------------------|-------------|
| `id`          | `SERIAL` (INT4)            | `PRIMARY KEY`          | Auto-incrementing identifier |
| `short_code`  | `VARCHAR`                  | `NOT NULL`             | Short code that was clicked (indexed) |
| `clicked_at`  | `TIMESTAMP WITH TIME ZONE` | `DEFAULT NOW()`        | ISO 8601 UTC timestamp of click (indexed) |
| `referrer`    | `TEXT`                     | `NULL`                 | HTTP Referer header (nullable) |
| `user_agent`  | `TEXT`                     | `NULL`                 | Client User-Agent header (nullable) |
| `client_ip`   | `TEXT`                     | `NULL`                 | Client IP address (nullable) |
| `metadata`    | `JSONB`                    | `DEFAULT '{}'::jsonb`  | Reserved for future extensible fields |

---

## 2. Raw SQL Insert Contract (`psycopg2`)

The Lambda worker should use the following parameterized SQL query:

```python
import json
import psycopg2

INSERT_SQL = """
INSERT INTO analytics (short_code, clicked_at, referrer, user_agent, client_ip, metadata)
VALUES (%s, %s, %s, %s, %s, %s);
"""

# Example execution in Lambda handler:
def insert_click_event(cursor, event_data: dict):
    cursor.execute(
        INSERT_SQL,
        (
            event_data["short_code"],
            event_data["timestamp"],  # ISO 8601 string, e.g. "2026-09-17T07:15:00Z"
            event_data.get("referrer"),
            event_data.get("user_agent"),
            event_data.get("client_ip"),
            json.dumps(event_data.get("metadata", {}))
        )
    )
```

---

## 3. Incoming SQS Message JSON Schema

The message body received from the SQS queue contains a JSON object emitted by `api-service`:

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
