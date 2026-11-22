"""Cancel Pending orders older than PENDING_ORDER_TTL_MINUTES and release their stock reserve."""
from app.db.session import get_session
from app.services import order_service


def main() -> None:
    session = get_session()
    total = 0
    try:
        # Batches of 100 (see lock_stale_pending_orders); commit each so locks are short.
        while n := order_service.expire_stale_orders(session):
            session.commit()
            total += n
    finally:
        session.close()
    print(f"Expired pending orders: {total}")


if __name__ == "__main__":
    main()
