from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    question = relationship(
        "Question", back_populates="owner", cascade="all, delete-orphan"
    )
    choices = relationship(
        "Choice", back_populates="answered_by", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True)
    question_text = Column(String(200))
    pub_date = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    choices = relationship("Choice", back_populates="question")
    owner = relationship("User", back_populates="question")


class Choice(Base):
    __tablename__ = "choice"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("question.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    choice_text = Column(String(200))
    votes = Column(Integer, default=0)

    question = relationship("Question", back_populates="choices")

    answered_by = relationship("User", back_populates="choices")
