from sqlalchemy import Column, DateTime, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AnalyticsClick(Base):
    """
    Model representing click events on shortened URLs.
    Owned exclusively by analytics-backend.
    """
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    short_code = Column(String(32), nullable=False, index=True)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    referrer = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    client_ip = Column(Text, nullable=True)
    metadata_json = Column("metadata", JSONB, server_default=text("'{}'::jsonb"), nullable=False)
