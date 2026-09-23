import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

import redis
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import URL
from .sqs import publish_click_event
from .utils import encode_base62, setup_json_logging

# Configure structured JSON logging
setup_json_logging(settings.LOG_LEVEL)
logger = logging.getLogger("api_service")

# Initialize Redis client with connection pooling
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify Redis connection on startup
    try:
        redis_client.ping()
        logger.info("Connected to Redis successfully", extra={"extra_fields": {"redis_url": settings.REDIS_URL}})
    except Exception as e:
        logger.warning("Could not connect to Redis on startup", extra={"extra_fields": {"error": str(e)}})
    yield
    # Cleanup Redis connection on shutdown
    try:
        redis_client.close()
    except Exception:
        pass


app = FastAPI(
    title="URL Shortener API Service",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Expose Prometheus metrics (/metrics) for request counts and latency histograms
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


class ShortenRequest(BaseModel):
    url: str


class ShortenResponse(BaseModel):
    short_url: str


@app.get("/healthz", status_code=status.HTTP_200_OK, tags=["Health"])
def healthz():
    """Kubernetes liveness and readiness probe endpoint."""
    return {"status": "ok"}


@app.post("/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED, tags=["Shortener"])
def shorten_url(payload: ShortenRequest, db: Session = Depends(get_db)):
    """
    Creates a shortened URL.
    1. Inserts the original URL to obtain the auto-generated database sequence ID.
    2. Base62 encodes the ID into a concise short_code.
    3. Persists the short_code to the row.
    4. Returns the full shortened URL.
    """
    raw_url = payload.url.strip()
    if not raw_url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")

    try:
        new_url_entry = URL(original_url=raw_url)
        db.add(new_url_entry)
        db.flush()  # Populates new_url_entry.id from the database sequence

        # Encode the sequence ID using base62 (~10 lines, no external library)
        short_code = encode_base62(new_url_entry.id)
        new_url_entry.short_code = short_code
        db.commit()
        db.refresh(new_url_entry)

        short_url = f"{settings.BASE_URL.rstrip('/')}/{short_code}"
        logger.info(
            "URL shortened successfully",
            extra={"extra_fields": {"id": new_url_entry.id, "short_code": short_code, "original_url": raw_url}},
        )
        return ShortenResponse(short_url=short_url)
    except Exception as e:
        db.rollback()
        logger.error("Failed to shorten URL", extra={"extra_fields": {"error": str(e)}}, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to shorten URL")


@app.get("/{short_code}", tags=["Redirect"])
def redirect_to_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Resolves a short_code to its original long URL and issues an HTTP 302 redirect.
    1. Checks Redis cache first.
    2. On cache miss, queries Postgres and caches the result with a 1-hour TTL.
    3. Asynchronously emits a click event to SQS via BackgroundTasks without blocking the 302 response.
    """
    original_url: Optional[str] = None

    # Step 1: Check Redis cache
    try:
        original_url = redis_client.get(short_code)
    except Exception as e:
        logger.warning(
            "Redis lookup failed, falling back to database",
            extra={"extra_fields": {"short_code": short_code, "error": str(e)}},
        )

    # Step 2: Cache miss -> query Postgres
    if not original_url:
        record = db.query(URL).filter(URL.short_code == short_code).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")

        original_url = record.original_url

        # Populate Redis with a 1-hour (3600s) TTL
        try:
            redis_client.set(short_code, original_url, ex=settings.REDIS_TTL_SECONDS)
        except Exception as e:
            logger.warning(
                "Failed to write to Redis cache",
                extra={"extra_fields": {"short_code": short_code, "error": str(e)}},
            )

    # Extract client headers for analytics
    referrer = request.headers.get("referer")
    user_agent = request.headers.get("user-agent")
    client_ip = request.headers.get("x-forwarded-for")
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    elif request.client:
        client_ip = request.client.host
    else:
        client_ip = None

    timestamp = datetime.now(timezone.utc).isoformat()

    # Step 3: Publish event to SQS asynchronously (non-blocking background task)
    background_tasks.add_task(
        publish_click_event,
        short_code=short_code,
        timestamp=timestamp,
        referrer=referrer,
        user_agent=user_agent,
        client_ip=client_ip,
    )

    # Step 4: Issue HTTP 302 redirect immediately
    return RedirectResponse(url=original_url, status_code=status.HTTP_302_FOUND)
