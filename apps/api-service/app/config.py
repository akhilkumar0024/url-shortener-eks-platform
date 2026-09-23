import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/shortener"
    )

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/0"
    )
    REDIS_TTL_SECONDS: int = int(os.getenv("REDIS_TTL_SECONDS", "3600"))

    # SQS
    SQS_QUEUE_URL: str = os.getenv("SQS_QUEUE_URL", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    MOCK_SQS: bool = os.getenv("MOCK_SQS", "true").lower() in ("true", "1", "yes")

    # App
    BASE_URL: str = os.getenv("BASE_URL", "https://mymegham.cloud")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        case_sensitive = True


settings = Settings()
