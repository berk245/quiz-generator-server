from sqlalchemy import Column, String, Boolean, DateTime, BIGINT
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    user_id = Column(BIGINT, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=1)
    member_since = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
