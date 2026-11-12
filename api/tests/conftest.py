import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import engine, SessionLocal
from app.dependencies import get_db
from app.core.limiter import limiter


@pytest.fixture()
def db_session():
    """Wrap each test in an outer transaction that is always rolled back.

    create_savepoint: the code's commit()/rollback() only release/roll back a SAVEPOINT,
    so a rollback after an IntegrityError does not wipe data created earlier in the test.
    """
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = SessionLocal(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    outer_transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    limiter.reset()  # avoid 429s from state left over by previous test runs

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
