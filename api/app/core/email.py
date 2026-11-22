import logging
from app.core.config import settings

logger = logging.getLogger("app.email")


def send_email(to: str, subject: str, body: str) -> None:
    if settings.app_env == "dev":
        logger.info("EMAIL to=%s subject=%s\n%s", to, subject, body)
    else:
        logger.info("EMAIL subject=%s", subject)