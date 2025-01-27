from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from backend.db_depends import get_db
from models.catalog import Product, Category
from models.user import User
from routes.user import get_current_user_or_none
from schemas.catalog import CreateCategory, UpdateCategory, CreateProduct
from backend.config import templates

router = APIRouter()


@router.post("/categories/", response_model=CreateCategory)
async def create_category(category: CreateCategory, db: Session = Depends(get_db)):
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/categories/{category_id}", response_model=UpdateCategory)
async def update_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/products/", response_model=CreateProduct)
async def create_product(product: CreateProduct, db: Session = Depends(get_db)):
    db_product = Product(name=product.name, price=product.price, image=product.image, description=product.description,
                         category_id=product.category_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"detail": "Product deleted successfully"}


@router.get("/showcase/", response_class=HTMLResponse)
async def read_products(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_none)
):
    all_product = db.query(Product).all()

    context = {"request": request, "products": all_product}
    if current_user:
        context["current_user"] = current_user

    return templates.TemplateResponse("showcase.html", context)
