from sqlalchemy.orm import relationship
from backend.db import Base
from sqlalchemy import Column, String, Integer, Text, ForeignKey


class Cart(Base):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    products = relationship('CartItem', backref='cart', lazy=True, cascade="all, delete-orphan")

    def total_quantity(self):
        return sum(item.quantity for item in self.products)


class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('carts.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    product = relationship('Product', backref='cart_items', lazy=True)

    def update_quantity(self, new_quantity):
        if new_quantity > 0:
            self.quantity = new_quantity
        else:
            raise ValueError("Quantity must be greater than zero.")


