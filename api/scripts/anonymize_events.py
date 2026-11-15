from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.db.session import get_session
from app.repositories import telemetry_repository


def main() -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.event_retention_days)
    session = get_session()
    try:
        counts = telemetry_repository.anonymize_older_than(session, cutoff)
        session.commit()
    finally:
        session.close()
    print(f"Anonymised before {cutoff:%Y-%m-%d}: {counts}")


if __name__ == "__main__":
    main()
