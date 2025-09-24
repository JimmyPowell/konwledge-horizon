from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import settings

engine = create_engine(settings.mysql_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_mysql_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
