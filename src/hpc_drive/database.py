from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .config import settings
from .models import Base  # Import Base from our snake_case models

# We need connect_args for SQLite
engine = create_engine(
    settings.DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
)

# This is the factory for our sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db_and_tables():
    # This will create all tables that inherit from Base
    Base.metadata.create_all(bind=engine)


# This is our new FastAPI dependency
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
