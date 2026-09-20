import json
import logging
from typing import Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .config import settings

logger = logging.getLogger("api_service.sqs")

# SQS client initialized lazily if not mocking
_sqs_client = None


def get_sqs_client():
    global _sqs_client
    if _sqs_client is None and not settings.MOCK_SQS and settings.SQS_QUEUE_URL:
        _sqs_client = boto3.client("sqs", region_name=settings.AWS_REGION)
    return _sqs_client


def publish_click_event(
    short_code: str,
    timestamp: str,
    referrer: Optional[str],
    user_agent: Optional[str],
    client_ip: Optional[str],
):
    """
    Publishes a click event message to AWS SQS.
    This function is executed asynchronously as a FastAPI BackgroundTask,
    guaranteeing zero latency or blocking on the HTTP 302 redirect response.

    SQS Message JSON Payload Contract:
    ----------------------------------
    {
        "short_code": "<str>",              # Required
        "timestamp": "<ISO 8601 UTC str>",  # e.g. "2026-09-17T07:15:00.123456+00:00"
        "referrer": "<str | null>",         # Extracted from HTTP 'Referer' header
        "user_agent": "<str | null>",       # Extracted from HTTP 'User-Agent' header
        "client_ip": "<str | null>",        # Client IP (X-Forwarded-For or socket IP)
        "metadata": {}                      # Extensible JSON metadata object
    }
    """
    payload = {
        "short_code": short_code,
        "timestamp": timestamp,
        "referrer": referrer,
        "user_agent": user_agent,
        "client_ip": client_ip,
        "metadata": {},
    }

    if settings.MOCK_SQS:
        logger.info(
            "MOCK_SQS is enabled: Click event logged and skipped SQS publishing",
            extra={"extra_fields": {"click_event": payload, "mock_sqs": True}},
        )
        return

    if not settings.SQS_QUEUE_URL:
        logger.warning(
            "SQS_QUEUE_URL is not set and MOCK_SQS is False; dropping event",
            extra={"extra_fields": {"short_code": short_code}},
        )
        return

    try:
        sqs = get_sqs_client()
        if sqs:
            sqs.send_message(
                QueueUrl=settings.SQS_QUEUE_URL,
                MessageBody=json.dumps(payload),
            )
            logger.info(
                "Click event published to SQS successfully",
                extra={"extra_fields": {"short_code": short_code, "queue_url": settings.SQS_QUEUE_URL}},
            )
    except (BotoCoreError, ClientError) as e:
        logger.error(
            "Failed to publish click event to SQS",
            extra={"extra_fields": {"short_code": short_code, "error": str(e)}},
            exc_info=True,
        )
