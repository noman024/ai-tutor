from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import Base
from backend.app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 