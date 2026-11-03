import pytest
from sqlalchemy import event
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import engine, SessionLocal
from app.dependencies import get_db
from app.core.limiter import limiter


@pytest.fixture()
def db_session():
    """Wrap each test in a transaction + SAVEPOINT so that db.commit() calls
    made by the code under test do not actually persist anything."""
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = SessionLocal(bind=connection)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, transaction):
        if transaction.nested and not transaction._parent.nested:
            sess.begin_nested()

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
