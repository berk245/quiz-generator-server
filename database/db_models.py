from sqlalchemy import Column, ForeignKey, String, Boolean, DateTime, INT
from sqlalchemy.dialects.mysql import LONGTEXT, ENUM
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'User'
    user_id = Column(INT, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=1)
    member_since = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    quizzes = relationship("Quiz", back_populates='user')
    sources = relationship("Source", back_populates='user')


class Quiz(Base):
    __tablename__ = 'Quiz'
    quiz_id = Column(INT, primary_key=True, autoincrement=True)
    user_id = Column(INT, ForeignKey('User.user_id'), nullable=False)
    quiz_title = Column(String, nullable=False)
    quiz_description = Column(LONGTEXT, nullable=True)
    keywords = Column(LONGTEXT, nullable=True)
    meta_prompt = Column(LONGTEXT, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, nullable=False, default=1)

    # Define the many-to-one relationship
    user = relationship("User", back_populates="quizzes")
    quiz_sources = relationship("QuizSource", back_populates="quiz")

    # Define the one-to-many relationship
    questions = relationship("Question", back_populates="quiz")


class Source(Base):
    __tablename__ = 'Source'
    source_id = Column(INT, primary_key=True, autoincrement=True)
    user_id = Column(INT, ForeignKey('User.user_id'), nullable=False)
    file_hash = Column(String, nullable=False, unique=True)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="sources")
    quiz_sources = relationship("QuizSource", back_populates="source")


class QuizSource(Base):
    __tablename__ = 'QuizSource'
    quiz_source_id = Column(INT, primary_key=True, autoincrement=True)
    source_id = Column(INT, ForeignKey('Source.source_id'), nullable=False)
    quiz_id = Column(INT, ForeignKey('Quiz.quiz_id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    source = relationship("Source", back_populates="quiz_sources")
    quiz = relationship("Quiz", back_populates="quiz_sources")


class Question(Base):
    __tablename__ = 'Question'

    question_id = Column(INT, primary_key=True, autoincrement=True)
    quiz_id = Column(INT, ForeignKey('Quiz.quiz_id'), nullable=False)
    instructions = Column(LONGTEXT, nullable=True)
    question_type = Column(ENUM('multi'), nullable=False)
    question_text = Column(LONGTEXT, nullable=False)
    multiple_choices = Column(LONGTEXT, nullable=True)
    correct_answer = Column(LONGTEXT, nullable=True)
    difficulty = Column(ENUM('easy', 'medium', 'hard'), nullable=True)
    score = Column(INT, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
     
    # Define the many-to-one relationship
    quiz = relationship("Quiz", back_populates="questions")
