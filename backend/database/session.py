"""
Database session management and SQLite WAL engine configuration.
"""

from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.config.settings import settings
from backend.config.logging_config import logger

Base = declarative_base()


def get_engine():
    """Initializes SQLAlchemy engine with SQLite WAL pragmas."""
    db_url = settings.DATABASE_URL

    # Ensure parent directory exists for SQLite
    if db_url.startswith("sqlite:///"):
        db_path = Path(db_url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}

    engine = create_engine(
        db_url,
        echo=settings.SQL_ECHO,
        connect_args=connect_args,
        pool_pre_ping=True
    )

    # Configure SQLite PRAGMA commands for WAL mode concurrency
    if "sqlite" in db_url:
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-64000")  # 64 MB cache
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=5000")  # 5s retry timeout
            cursor.close()
            logger.debug("SQLite WAL and performance pragmas initialized.")

    return engine


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Creates all database tables defined in the metadata."""
    import backend.database.models  # Ensure models are imported
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")


def get_db():
    """FastAPI dependency for yielding database sessions."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
