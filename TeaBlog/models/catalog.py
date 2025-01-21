from sqlalchemy.orm import relationship
from backend.db import Base
from sqlalchemy import Column, String, Integer, ForeignKey


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, index=True, primary_key=True)
    name = Column(String, unique=True, index=True)
    products = relationship('Product', back_populates='category')


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, index=True, primary_key=True)
    name = Column(String, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(Integer)
    image = Column(String)
    description = Column(String(1000), nullable=True)
    category = relationship("Category", back_populates="products")
