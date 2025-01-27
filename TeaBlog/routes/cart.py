from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from backend.db_depends import get_db
from models.cart import Cart, CartItem
from fastapi.responses import HTMLResponse, Response
from models.catalog import Product
from backend.config import templates
from models.user import User
from routes.user import get_current_user_or_none
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def view_cart(request: Request, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user_or_none)):
    if not current_user:
        return templates.TemplateResponse("unauthorized.html", {
            "request": request})  # Отправляем на страницу с сообщением о необходимости авторизации

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    items = cart.products if cart else []
    context = {"request": request, "items": items, "cart": cart, "current_user": current_user}
    return templates.TemplateResponse("cart_view.html", context)


@router.post("/add/{product_id}")
async def add_to_cart(
        product_id: int,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_none),
        quantity: int = 1  # Устанавливаем значение по умолчанию
):
    # Получаем количество из тела запроса
    body = await request.json()
    quantity = body.get("quantity", quantity)  # Если quantity не передан, используем значение по умолчанию

    if current_user:
        cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.add(cart)
            db.commit()
            db.refresh(cart)

        cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            db.add(cart_item)

        db.commit()
        print(f"Добавление товара с ID {product_id} пользователем {current_user.id}")
        return {"message": "Товар добавлен в корзину"}
    else:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Пожалуйста, авторизуйтесь.")


@router.post("/update_cart_item/{item_id}")
async def update_cart_item(
        item_id: int,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_none)
):
    body = await request.json()
    cart_id = body.get("cart_id")
    quantity = body.get("quantity")

    if current_user:
        cart_item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart_id).first()
        if not cart_item:
            raise HTTPException(status_code=404, detail="Элемент корзины не найден")

        cart_item.quantity = quantity  # Обновляем количество
        db.commit()
        return {"message": "Количество обновлено"}
    else:
        raise HTTPException(status_code=403, detail="Доступ запрещен. Пожалуйста, авторизуйтесь.")


@router.get("/remove_cart_item/{cart_id}/{item_id}")
async def remove_cart_item(cart_id: int, item_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(cart_item)
    db.commit()
    return {"message": "Товар удален из корзины"}


@router.delete("/{cart_id}", status_code=204)
async def delete_cart(
        cart_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_none)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    cart = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == current_user.id).first()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    db.delete(cart)
    db.commit()

    return Response(status_code=204)


@router.get("/checkout", response_class=HTMLResponse)
async def checkout(request: Request, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user_or_none)):
    if current_user:
        cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    else:
        return templates.TemplateResponse("checkout.html", {"request": request, "items": [], "cart": None})

    if not cart:
        return templates.TemplateResponse("checkout.html", {"request": request, "items": [], "cart": cart})

    items = cart.products
    total_price = sum(item.product.price * item.quantity for item in items)

    return templates.TemplateResponse("checkout.html",
                                      {"request": request, "items": items, "cart": cart, "total_price": total_price})


@router.post("/checkout")
async def process_checkout(request: Request, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user_or_none)):
    form = await request.form()
    address = form.get("address")
    phone = form.get("phone")

    if current_user:
        cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
        if cart:
            # Здесь можно добавить логику для обработки заказа, например, сохранение в БД
            # После обработки заказа, удаляем корзину
            db.delete(cart)
            db.commit()
            return templates.TemplateResponse("checkout_success.html", {
                "request": request,
                "message": "Заказ успешно оформлен"
            })
    return {"message": "Ошибка при оформлении заказа"}
