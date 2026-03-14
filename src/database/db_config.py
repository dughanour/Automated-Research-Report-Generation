from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator
from src.logger import GLOBAL_LOGGER as log

# Database URL - change this for different databases
# SQLite for development (easy, no setup)
# PostgreSQL for production: "postgresql://user:password@localhost/dbname"
DATABASE_URL = "sqlite:///./app.db"

# Create engine
engine = create_engine(
 DATABASE_URL,
 connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models (User, etc.)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Automatically closes session after request completes.
    """
    db = SessionLocal()
    try:
        log.info("Database session created")
        yield db
    finally:
        db.close()
        log.info("Database session closed")