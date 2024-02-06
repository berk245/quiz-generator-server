import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from typing import Generator
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

db_uri = os.getenv('DATABASE_URI')
engine = create_engine(db_uri)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
