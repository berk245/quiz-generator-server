import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session, sessionmaker
from typing import Generator
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Now you can access the variables
db_uri = os.getenv('DATABASE_URI')
engine = create_engine(db_uri)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
