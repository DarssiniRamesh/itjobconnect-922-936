from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# PUBLIC_INTERFACE
def get_database_url():
    """Get the database URL from environment variable or default to SQLite."""
    return os.getenv("DATABASE_URL") or "sqlite:///./jobportal.db"

DATABASE_URL = get_database_url()

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create a configured session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
