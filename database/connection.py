# database/connection.py
# ============================================================
# Database connection pool, session factory, and helpers.
# ============================================================

from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from config import logger, settings
from database.models import Base


# ── Engine ───────────────────────────────────────────────────

def create_db_engine(database_url: str = None):
    """Create and return a SQLAlchemy engine."""
    url = database_url or settings.database_url
    engine = create_engine(
        url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,   # Verify connection is alive before using
        echo=False,           # Set True to log all SQL statements
    )
    return engine


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Session helpers ──────────────────────────────────────────

@contextmanager
def get_session() -> Session:
    """
    Context manager that yields a DB session and handles
    commit/rollback/close automatically.

    Usage:
        with get_session() as session:
            session.add(record)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def get_db():
    """
    FastAPI dependency — yields a DB session per request.

    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Schema management ────────────────────────────────────────

def create_all_tables():
    """Create all tables defined in models.py (idempotent)."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.success("All tables created (or already exist).")


def drop_all_tables():
    """Drop all tables — use only during development/reset."""
    logger.warning("Dropping all database tables!")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped.")


def test_connection() -> bool:
    """Verify the database connection is working."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.success(f"Database connection OK → {settings.database_url}")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
