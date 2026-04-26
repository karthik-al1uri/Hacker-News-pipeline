"""Database connection and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


def get_engine():
    """Create and return a SQLAlchemy engine from the DB_URL env variable.

    Returns:
        SQLAlchemy Engine instance.
    """
    db_url = os.getenv("DB_URL", "postgresql://user:password@localhost:5433/hn_trends")
    return create_engine(db_url)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def init_db() -> None:
    """Initialize the database by creating all tables.

    Returns:
        None
    """
    from storage.models import Story
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
