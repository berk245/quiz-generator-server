from sqlalchemy import Column, ForeignKey, String, Boolean, DateTime, BIGINT
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'User'
    user_id = Column(BIGINT, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=1)
    member_since = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    quizzes = relationship("Quiz", back_populates='user')

class Quiz(Base):
    __tablename__ = 'Quiz'
    quiz_id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey('User.user_id'),nullable=False)
    quiz_title = Column(String, nullable=False)
    quiz_description = Column(LONGTEXT, nullable=True)
    meta_prompt = Column(LONGTEXT, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, nullable=False, default=1)

    # Define the many-to-one relationship
    user = relationship("User", back_populates="quizzes")
