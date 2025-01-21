from typing import Optional
from pydantic import BaseModel, EmailStr


class CreateUser(BaseModel):
    username: str
    first_name: str
    email: EmailStr
    password: str


class UpdateUser(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
