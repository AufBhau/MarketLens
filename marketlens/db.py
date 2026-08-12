from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from marketlens.config import get_settings


class Base(DeclarativeBase):
    pass


def get_engine():
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    engine = get_engine()
    SessionLocal.configure(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    from marketlens import models  # noqa: F401

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
