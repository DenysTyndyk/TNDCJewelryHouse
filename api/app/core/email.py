import logging

logger = logging.getLogger("app.email")


def send_email(to: str, subject: str, body: str) -> None:
    logger.info("EMAIL to=%s subject=%s\n%s", to, subject, body)
