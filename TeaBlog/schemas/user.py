from typing import Optional
from pydantic import BaseModel, EmailStr

from models.user import User


class CreateUser(BaseModel):
    username: str
    first_name: str
    email: EmailStr
    password: str


class UpdateUser(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None  # Изменено на Optional


class UserInDB(User):
    hashed_password: str  # Здесь не требуется изменений, но убедитесь, что User имеет правильные аннотации
