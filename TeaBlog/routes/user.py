from typing import Annotated
from fastapi import APIRouter, Form, Depends, HTTPException, status, Request, Cookie, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from backend import db
from backend.config import templates
from backend.db_depends import get_db
from models.user import User
from schemas.user import TokenData
from passlib.context import CryptContext

router = APIRouter()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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

    hashed_password = get_password_hash(password)
    db_user = User(username=username, first_name=first_name, email=email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"detail": "User registered successfully"}


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


async def get_current_user_or_none(
        cookie_access_token: Annotated[str, Cookie()] = None,
        db: Session = Depends(get_db)
):
    if cookie_access_token is None:
        return None

    try:
        scheme, _, token = cookie_access_token.partition(" ")
        if scheme.lower() != "bearer":
            return None

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:
        return None

    user = get_user(db, username=token_data.username)
    if user is None:
        return None

    return user



def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.get("/", response_class=HTMLResponse)
async def read_home(
        request: Request,
        current_user: User = Depends(get_current_user_or_none)
):
    context = {"request": request}
    if current_user:
        context["current_user"] = current_user
    return templates.TemplateResponse("index.html", context)


@router.post("/login")
async def login(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    db_user = get_user(db, username)
    print(f"Attempting to log in user: {username}")

    if db_user and verify_password(password, db_user.password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.username}, expires_delta=access_token_expires
        )

        # Устанавливаем cookie с токеном
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(
            key="cookie_access_token",
            value=f"Bearer {access_token}",
            max_age=60 * 30,  # 30 минут
            secure=False,  # Установите True, если используете HTTPS
            httponly=False,
            samesite="lax"  # Или "strict" для строгого ограничения
        )
        print(f"Cookie set: Bearer {access_token}")
        return response
    else:
        print("Invalid credentials")
        raise HTTPException(status_code=400, detail="Invalid credentials")


@router.get("/logout")
async def logout(current_user: Annotated[User, Depends(get_current_user_or_none)]):
    response = RedirectResponse(url="/")
    response.delete_cookie(key='cookie_access_token')
    return response


@router.get("/user/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user_or_none)]):
    return current_user


@router.delete("/user/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User successfully deleted"}


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
