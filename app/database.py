from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


# SQLite (used by the test suite) only allows a connection on the thread that
# created it unless told otherwise; FastAPI runs sync routes in a thread pool.
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def utc_now() -> datetime:
    """Current UTC time as a naive datetime, matching the existing columns.

    Replaces datetime.utcnow(), which is deprecated since Python 3.12.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
