from typing import Optional
from pydantic import BaseModel


class CreateState(BaseModel):
    title: str
    content: str
    image_url: str


class UpdateState(BaseModel):
    title: Optional[str] = None
    content: Optional[str]
    image_url: Optional[str] = None