"""
SQLite and SQLAlchemy Database Connection Management.
Configures SQLite with WAL mode, foreign keys, and scoped sessions for thread safety.
"""
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import AppConfig
from utils.logger import get_logger

logger = get_logger("DatabaseConnection")

from sqlalchemy.pool import StaticPool

Base = declarative_base()
_engines = {}
_factories = {}

def get_engine(db_url: str = None):
    """Retrieve or configure SQLAlchemy SQLite engine cached by URL."""
    target_url = db_url or AppConfig.DATABASE_URL
    if target_url not in _engines:
        if ":memory:" in target_url:
            eng = create_engine(
                target_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            eng = create_engine(
                target_url,
                connect_args={"check_same_thread": False},
                echo=False
            )
        
        # Enable SQLite WAL and Foreign Keys for safety and concurrent read performance
        @event.listens_for(eng, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            try:
                if ":memory:" not in target_url:
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA foreign_keys=ON")
            finally:
                cursor.close()

        _engines[target_url] = eng
        _factories[target_url] = sessionmaker(bind=eng, autocommit=False, autoflush=False)
        logger.info(f"Initialized database engine: {target_url}")
        
    return _engines[target_url]

def get_session_factory(db_url: str = None):
    """Get sessionmaker factory for given URL."""
    target_url = db_url or AppConfig.DATABASE_URL
    if target_url not in _factories:
        get_engine(target_url)
    return _factories[target_url]

@contextmanager
def get_db_session(db_url: str = None):
    """Context manager for database sessions with automatic commit/rollback."""
    factory = get_session_factory(db_url)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session rolled back due to error: {e}")
        raise
    finally:
        session.close()

def init_db(db_url: str = None):
    """Create all tables if they do not exist."""
    engine = get_engine(db_url)
    from database.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified and initialized successfully.")
