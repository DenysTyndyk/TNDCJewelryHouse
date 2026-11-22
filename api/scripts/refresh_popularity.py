from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.db.session import get_session
from app.repositories import catalog_repository

def main() -> None:
    since = datetime.now(timezone.utc) - timedelta(days=settings.reco_popularity_long_days)
    session = get_session()
    try:
        changed = catalog_repository.refresh_view_counts(session,since)
        session.commit()
    finally:
        session.close()
    print(f"view_count refreshed from {since:%Y-%m-%d}: {changed} products changed")

if __name__ == "__main__":
    main()
