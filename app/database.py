import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./patients.db")

# Standard SQLite requires check_same_thread=False for multi-threaded FastAPI execution.
connect_args = {}
if DATABASE_URL.startswith("sqlite:"):
    connect_args["check_same_thread"] = False

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
except Exception as e:
    logger.warning(f"Failed to initialize database with URL {DATABASE_URL}: {e}. Falling back to local SQLite.")
    FALLBACK_URL = "sqlite:///./patients.db"
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
