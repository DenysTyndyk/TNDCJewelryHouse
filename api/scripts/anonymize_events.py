from app.db.session import get_session
from app.services import order_service


def main() -> None:
    session = get_session()
    total = 0
    try:
        while n := order_service.expire_stale_orders(session):
            session.commit()
            total += n
    finally:
        session.close()
    print(f"Expired pending orders: {total}")


if __name__ == "__main__":
    main()
