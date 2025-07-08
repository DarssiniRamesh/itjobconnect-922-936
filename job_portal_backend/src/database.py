from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# PUBLIC_INTERFACE
def get_database_url():
    """
    Get the database URL from environment variable or default to SQLite.
    - Use the DATABASE_URL environment variable if set. This should be a SQLAlchemy-compatible database URL string,
      e.g. postgresql://user:password@host:port/dbname or mysql+mysqlconnector://user:pass@host/db.
      For SQLite, use sqlite:///./jobportal.db or similar.
    - If DATABASE_URL is not defined, default to SQLite file db for development.
    """
    return os.getenv("DATABASE_URL") or "sqlite:///./jobportal.db"

DATABASE_URL = get_database_url()

# PUBLIC_INTERFACE
def get_engine():
    """
    Return a SQLAlchemy engine configured from DATABASE_URL.
    Special options (like check_same_thread) are set for SQLite only.
    """
    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    return create_engine(DATABASE_URL, connect_args=connect_args)

engine = get_engine()

# Create a configured session class (use this for session dependency)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# ----- Notes for Externalization -----
# To use an external DB (e.g. Postgres, MySQL):
#   1. Set the environment variable DATABASE_URL. Example:
#         export DATABASE_URL="postgresql://jobuser:jobpass@dbhost:5432/jobportal"
#   2. Ensure external DB is running and accessible from backend's network.
#   3. Alembic migrations and all code use the same DATABASE_URL.
#   4. For production, secure credentials via secrets manager or orchestration platform.
#
# When integrating with a managed 'job_portal_database' service,
#   simply set DATABASE_URL to that service's connection string.
