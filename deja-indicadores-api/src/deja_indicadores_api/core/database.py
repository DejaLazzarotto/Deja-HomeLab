from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from deja_indicadores_api.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Classe-base dos modelos persistentes da aplicação."""


def get_db_session() -> Generator[Session, None, None]:
    """Fornece uma sessão de banco de dados por requisição."""

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
