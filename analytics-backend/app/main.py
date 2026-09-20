import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import desc, func, text
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import AnalyticsClick
from .utils import setup_json_logging

# Configure structured JSON logging
setup_json_logging(settings.LOG_LEVEL)
logger = logging.getLogger("analytics_backend")

app = FastAPI(
    title="URL Shortener Analytics Backend",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Enable CORS for configured frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ClickItem(BaseModel):
    short_code: str
    clicked_at: datetime
    referrer: Optional[str]
    user_agent: Optional[str]
    client_ip: Optional[str]

    class Config:
        from_attributes = True


class ClicksResponse(BaseModel):
    items: List[ClickItem]
    total: int
    limit: int
    offset: int


class ShortCodeStat(BaseModel):
    short_code: str
    total_clicks: int


class TimeBucketStat(BaseModel):
    time_bucket: str
    click_count: int


class StatsResponse(BaseModel):
    by_short_code: List[ShortCodeStat]
    by_time: List[TimeBucketStat]


@app.get("/healthz", status_code=status.HTTP_200_OK, tags=["Health"])
def healthz():
    """Health check endpoint for container probes."""
    return {"status": "ok"}


@app.get("/clicks", response_model=ClicksResponse, tags=["Analytics"])
def get_recent_clicks(
    limit: int = Query(50, ge=1, le=500, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
):
    """
    Returns recent click events as JSON, sorted with newest clicks first and paginated.
    """
    total_count = db.query(func.count(AnalyticsClick.id)).scalar() or 0

    records = (
        db.query(AnalyticsClick)
        .order_by(desc(AnalyticsClick.clicked_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return ClicksResponse(
        items=[
            ClickItem(
                short_code=r.short_code,
                clicked_at=r.clicked_at,
                referrer=r.referrer,
                user_agent=r.user_agent,
                client_ip=r.client_ip,
            )
            for r in records
        ],
        total=total_count,
        limit=limit,
        offset=offset,
    )


@app.get("/stats", response_model=StatsResponse, tags=["Analytics"])
def get_click_stats(db: Session = Depends(get_db)):
    """
    Returns aggregated analytics:
    1. Total click counts grouped by short_code.
    2. Click counts grouped by hourly time buckets (chronological).
    """
    # Group by short_code
    code_results = (
        db.query(
            AnalyticsClick.short_code,
            func.count(AnalyticsClick.id).label("total_clicks"),
        )
        .group_by(AnalyticsClick.short_code)
        .order_by(desc(text("total_clicks")))
        .all()
    )
    by_short_code = [
        ShortCodeStat(short_code=row[0], total_clicks=row[1])
        for row in code_results
    ]

    # Group by hourly time bucket
    # PostgreSQL date_trunc('hour', clicked_at)
    time_results = (
        db.query(
            func.date_trunc("hour", AnalyticsClick.clicked_at).label("time_bucket"),
            func.count(AnalyticsClick.id).label("click_count"),
        )
        .group_by(text("time_bucket"))
        .order_by(text("time_bucket ASC"))
        .all()
    )
    by_time = [
        TimeBucketStat(
            time_bucket=row[0].isoformat() if hasattr(row[0], "isoformat") else str(row[0]),
            click_count=row[1],
        )
        for row in time_results
    ]

    return StatsResponse(
        by_short_code=by_short_code,
        by_time=by_time,
    )
