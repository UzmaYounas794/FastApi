from sqlalchemy.orm import Session
import os
from typing import Optional
from datetime import datetime, timedelta

from .models import Question, Choice

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import  jwt


from . import models, schemas

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
JWT_SECRET = "myjwtsecret"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, uid: int):
    return db.query(models.User).filter(models.User.id == uid).first()


def get_question_obj(db, qid):
    obj = get_question(db=db, qid=qid)
    if obj is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return obj

def get_user_obj(db, uid):
    obj = get_user_by_id(db=db, uid=uid)
    if obj is None:
        raise HTTPException(status_code=404, detail="User not found")
    return obj


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.hashed_password)

    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt



def create_question(db: Session, question: schemas.QuestionCreate):
    obj = Question(**question.dict())
    db.add(obj)
    db.commit()
    return obj


def get_question(db: Session, qid: int):
    return db.query(Question).filter(Question.id == qid).first()


def get_all_questions(db: Session):
    return db.query(Question).all()


def edit_question(db: Session, qid, question: schemas.QuestionCreate):
    obj = db.query(Question).filter(Question.id == qid).first()
    obj.question_text = question.question_text
    obj.pub_date = question.pub_date
    db.commit()
    return obj


def delete_question(db: Session, qid):
    db.query(Question).filter(Question.id == qid).delete()
    db.commit()


def create_choices(db: Session, qid: int, choice: schemas.ChoiceCreate):
    obj = Choice(**choice.dict())
    obj.question_id = qid
    db.add(obj)
    db.commit()
    return obj


def update_vote(choice_id: int, db: Session):
    obj = db.query(Choice).filter(Choice.id == choice_id).first()
    obj.votes += 1
    db.commit()
    return obj
