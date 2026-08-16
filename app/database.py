import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Monkeypatch sqlitecloud.dbapi2.Connection.create_function to handle SQLAlchemy's deterministic=True keyword arg
try:
    import sqlitecloud.dbapi2 as sqlitecloud_db2
    _orig_create_function = sqlitecloud_db2.Connection.create_function

    def _safe_create_function(self, name, num_params, func, *args, **kwargs):
        try:
            return _orig_create_function(self, name, num_params, func)
        except Exception:
            pass

    sqlitecloud_db2.Connection.create_function = _safe_create_function
except Exception as patch_err:
    logger.warning(f"Could not patch sqlitecloud.dbapi2: {patch_err}")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./patients.db")

try:
    if DATABASE_URL.startswith("sqlitecloud://"):
        import sqlitecloud
        engine = create_engine(
            "sqlite://",
            creator=lambda: sqlitecloud.connect(DATABASE_URL)
        )
    else:
        connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite:") else {}
        engine = create_engine(DATABASE_URL, connect_args=connect_args)
except Exception as e:
    logger.warning(f"Failed to initialize database with URL {DATABASE_URL}: {e}. Falling back to SQLite.")
    FALLBACK_URL = "sqlite:///./patients.db" if not os.environ.get("VERCEL") else "sqlite:///:memory:"
    engine = create_engine(FALLBACK_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that yields a database session for request lifecycle."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
