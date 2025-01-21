from pydantic import BaseModel
from typing import List, Optional


class CreateCategory(BaseModel):
    name: str


class UpdateCategory(BaseModel):
    name: str


class CreateProduct(BaseModel):
    name: str
    price: int
    image: str
    description: Optional[str] = None
    category_id: int


class UpdateProduct(BaseModel):
    name: str
    price: int
    image: str
    description: Optional[str] = None
