from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import settings
from .models import Base 

# pool_pre_ping=True prevents "MySQL server has gone away" 
# errors when containers restart or connections idle.
engine = create_engine(
    settings.DATABASE_URL, 
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
