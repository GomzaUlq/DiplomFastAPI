from backend.db import Base
from sqlalchemy import Column, String, Integer, Boolean


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64))
    first_name = Column(String(30))
    email = Column(String(120), nullable=False)
    password = Column(String(128), nullable=False)
    is_superuser = Column(Boolean(), default=False)
    is_active = Column(Boolean(), default=True)
