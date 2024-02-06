from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session, sessionmaker
from typing import Generator

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:2145under@localhost/qgen_local"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
