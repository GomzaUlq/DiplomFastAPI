from pydantic import BaseModel
from typing import List, Optional


#class CartItemBase(BaseModel):
#    product_id: int
#    quantity: int
#
#
#class CartItemCreate(CartItemBase):
#    pass
#
#
#class CartItem(CartItemBase):
#    id: int
#
#    class Config:
#        orm_mode = True
#
#
#class CartBase(BaseModel):
#    user_id: int
#
#
#class CartCreate(CartBase):
#    products: List[CartItemCreate]
#
#
#class Cart(CartBase):
#    id: int
#    products: List[CartItem] = []
#
#    class Config:
#        orm_mode = True
#