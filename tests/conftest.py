import os
import tempfile

# Point the app at a throwaway test database BEFORE any app module is imported.
# This is set unconditionally so the suite can never touch a dev database from
# a .env file. CI sets TEST_DATABASE_URL to a real Postgres service.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    f"sqlite:///{os.path.join(tempfile.gettempdir(), 'finflow_test.db')}",
)
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ENVIRONMENT"] = "test"

import fakeredis  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app.main as main_module  # noqa: E402
import app.services.analytics_service as analytics_service  # noqa: E402
import app.services.transaction_service as transaction_service  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_database():
    """Give every test an empty schema."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    """Swap the real Redis client for an in-memory one everywhere it is used."""
    client = fakeredis.FakeRedis(decode_responses=True)
    for module in (main_module, analytics_service, transaction_service):
        monkeypatch.setattr(module, "redis_client", client)
    return client


class BrokenRedis:
    """Stands in for a Redis server that is down."""

    def __getattr__(self, name):
        def fail(*args, **kwargs):
            raise ConnectionError("Redis is down")
        return fail


@pytest.fixture
def broken_redis(monkeypatch):
    client = BrokenRedis()
    for module in (main_module, analytics_service, transaction_service):
        monkeypatch.setattr(module, "redis_client", client)
    return client


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
