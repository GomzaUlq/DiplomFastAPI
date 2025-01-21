from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from backend.db_depends import get_db
from models.cart import Cart, CartItem
from fastapi.responses import HTMLResponse
from models.catalog import Product
from backend.config import templates


#@router.get("/cart", response_class=HTMLResponse)
#async def view_cart(request: Request, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
#    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
#    if not cart:
#        return templates.TemplateResponse("cart.html", {"request": request, "items": [], "cart": cart})
#
#    items = cart.products
#    return templates.TemplateResponse("cart.html", {"request": request, "items": items, "cart": cart})
#
#
#@router.post("/cart/add/{product_id}")
#async def add_to_cart(product_id: int, quantity: int, db: Session = Depends(get_db),
#                      user_id: int = Depends(get_current_user)):
#    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
#    if not cart:
#        cart = Cart(user_id=user_id)
#        db.add(cart)
#        db.commit()
#        db.refresh(cart)
#
#    cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()
#    if cart_item:
#        cart_item.quantity += quantity
#    else:
#        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
#        db.add(cart_item)
#
#    db.commit()
#    return {"message": "Товар добавлен в корзину"}
#
#
#@router.post("/cart/update/{cart_id}/{item_id}")
#async def update_cart_item(cart_id: int, item_id: int, quantity: int, db: Session = Depends(get_db)):
#    cart_item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart_id).first()
#    if not cart_item:
#        raise HTTPException(status_code=404, detail="Item not found")
#
#    cart_item.update_quantity(quantity)
#    db.commit()
#    return {"message": "Количество обновлено"}
#
#
#@router.get("/cart/remove/{cart_id}/{item_id}")
#async def remove_cart_item(cart_id: int, item_id: int, db: Session = Depends(get_db)):
#    cart_item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart_id).first()
#    if not cart_item:
#        raise HTTPException(status_code=404, detail="Item not found")
#
#    db.delete(cart_item)
#    db.commit()
#    return {"message": "Товар удален из корзины"}
