from fastapi import APIRouter, Cookie
from fastapi import Request, Form
from fastapi import Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from backend.config import templates
from backend.db_depends import get_db
from models.user import User
from schemas.user import UpdateUser
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
sessions = {}


@router.post("/register")
async def register(
        username: str = Form(...),
        email: str = Form(...),
        first_name: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, first_name=first_name, email=email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return RedirectResponse(url="/login", status_code=303)


@router.post("/login")
async def login(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user or not pwd_context.verify(password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Сохраняем сессию
    sessions[username] = db_user
    return RedirectResponse(url="/", status_code=303)


@router.get("/logout")
async def logout(username: str = Cookie(None)):
    if username in sessions:
        del sessions[username]
    return RedirectResponse(url="/", status_code=303)


@router.delete("/users/{user_id}")
async def delete_user(state_id: int, state: UpdateUser, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == state_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="State not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User успешно удалена"}


@router.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
