from datetime import datetime

from pydantic import BaseModel
from typing import Optional
from typing import List

from pydantic.errors import EmailError
from pydantic.networks import EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    full_name: str
    hashed_password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class ChoiceBase(BaseModel):
    choice_text: str
    votes: int


class ChoiceCreate(ChoiceBase):
    pass


class ChoiceList(ChoiceBase):
    id: int

    class Config:
        orm_mode = True


class QuestionBase(BaseModel):

    question_text: str
    pub_date: datetime


class QuestionCreate(QuestionBase):
    pass


class Question(QuestionBase):
    id: int

    class Config:
        orm_mode = True


class QuestionInfo(Question):
    choices: List[ChoiceList] = []
