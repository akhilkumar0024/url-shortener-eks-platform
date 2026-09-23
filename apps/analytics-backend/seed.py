import json
import logging
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, text
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed")

SAMPLE_SHORT_CODES = ["gh", "docs", "blog", "app", "status", "promo", "cloud"]
REFERRERS = [
    "https://news.ycombinator.com",
    "https://twitter.com",
    "https://github.com",
    "https://www.google.com",
    "https://linkedin.com",
    "https://reddit.com/r/programming",
    None,
]
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
]
IPS = [
    "192.168.1.102",
    "172.56.21.89",
    "10.0.4.15",
    "203.0.113.42",
    "198.51.100.7",
    "142.250.190.46",
    "104.244.42.1",
]


def seed_data():
    logger.info("Connecting to database: %s", settings.DATABASE_URL)
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # Check if table exists (should be created by alembic)
        result = conn.execute(
            text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'analytics');"
            )
        ).scalar()
        if not result:
            logger.error("Table 'analytics' does not exist! Please run migrations first.")
            return

        now = datetime.now(timezone.utc)
        logger.info("Generating 120 realistic click analytics records across past 24 hours...")

        insert_sql = text(
            """
            INSERT INTO analytics (short_code, clicked_at, referrer, user_agent, client_ip, metadata)
            VALUES (:short_code, :clicked_at, :referrer, :user_agent, :client_ip, :metadata)
            """
        )

        rows = []
        for i in range(120):
            # Spread across last 24 hours
            minutes_ago = random.randint(5, 24 * 60)
            clicked_at = now - timedelta(minutes=minutes_ago)
            short_code = random.choice(SAMPLE_SHORT_CODES)
            referrer = random.choice(REFERRERS)
            user_agent = random.choice(USER_AGENTS)
            client_ip = random.choice(IPS)

            rows.append(
                {
                    "short_code": short_code,
                    "clicked_at": clicked_at,
                    "referrer": referrer,
                    "user_agent": user_agent,
                    "client_ip": client_ip,
                    "metadata": json.dumps({}),
                }
            )

        for row in rows:
            conn.execute(insert_sql, row)

        conn.commit()
        logger.info("Successfully seeded %d analytics events!", len(rows))


if __name__ == "__main__":
    seed_data()
