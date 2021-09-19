from pollsapi.schemas import ChoiceList, QuestionInfo
from . import schemas
from . import models
from . import crud
from jose import JWTError, jwt
from fastapi.security import  OAuth2PasswordRequestForm

from datetime import timedelta
from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, status
from .database import SessionLocal, engine


from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

fake_secret_token = "coneofsilence"
models.Base.metadata.create_all(bind=engine)
import jwt

app = FastAPI()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(crud.oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid JWT",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, crud.JWT_SECRET, algorithms=[crud.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credential_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credential_exception
    return user

#
# @app.post("/login", response_model=schemas.Token)
# def login_for_access_token(
#     db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
# ):
#     user_data = crud.authenticate_user(db, form_data.username, form_data.password)
#     if not user_data:
#         raise HTTPException(
#             status.HTTP_401_UNAUTHORIZED,
#             detail="invalid email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     token_expires_date = timedelta(minutes=crud.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = crud.create_access_token(
#         data={"sub": user_data.email},
#         expires_delta=token_expires_date,
#     )
#     return {"access_token": access_token, "token_type": "bearer"}


@app.post("/signup/", response_model=schemas.User)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):

    user = crud.get_user_by_email(db, user_data.email)
    if user:
        raise HTTPException(status_code=409, detail="Email already registered.")
    signedup_user = crud.create_user(db, user_data)
    return signedup_user


@app.post("/token/", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user = crud.authenticate_user(db, form_data.username, form_data.password)

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=crud.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = crud.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/questions/", response_model=schemas.QuestionInfo)
def create_question(
    question: schemas.QuestionCreate,
    x_token: str = Header(...),
    #current_user: models.User = Depends(get_current_user),

    db: Session = Depends(get_db),
):
    if x_token != fake_secret_token:
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    return crud.create_question(db, question)


@app.get("/questions/", response_model=List[schemas.Question])
def get_questions(db: Session = Depends(get_db)):
    return crud.get_all_questions(db=db)



@app.get("/questions/{qid}", response_model=QuestionInfo)
def get_question(
    qid: int,
    db: Session = Depends(get_db),
     x_token: str = Header(...),
    #current_user: models.User = Depends(get_current_user),
):
    if x_token != fake_secret_token:
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    return crud.get_question_obj(db=db, qid=qid)


@app.put("/questions/{qid}/", response_model=schemas.QuestionInfo)
def edit_question(
    qid: int,
    question: schemas.QuestionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # get_user_obj(db=db, uid=uid)
    user_created = crud.get_question_obj(db=db, qid=qid)

    if user_created.user_id == current_user:

        obj = crud.edit_question(db=db, qid=qid, question=question)
        return obj
    raise HTTPException(status_code=404, detail="sorry you cant update others post")


@app.delete("/questions/{qid}")
def delete_question(
    qid: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    user_created = crud.get_question_obj(db=db, qid=qid)
    if user_created.user_id == current_user:

        crud.delete_question(db=db, qid=qid)
        return {"detail": "Question deleted", "status_code": 204}
    raise HTTPException(status_code=404, detail="sorry you cant delete others post")


@app.post("/questions/{qid}/choice", response_model=ChoiceList)
def create_choice(
    qid: int,
    choice: schemas.ChoiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    crud.get_question_obj(db=db, qid=qid)
    return crud.create_choices(db=db, qid=qid, choice=choice)



@app.put("/choices/{choice_id}/vote", response_model=schemas.ChoiceList)
def update_vote(
    choice_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    return crud.update_vote(choice_id=choice_id, db=db)
