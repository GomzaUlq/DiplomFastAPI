from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, HTTPException, Request
from sqlalchemy.orm import Session
from backend.config import templates
from backend.db_depends import get_db
from fastapi.responses import HTMLResponse
from models.state import State
from models.user import User
from routes.user import get_current_user_or_none
from schemas.state import CreateState, UpdateState

router = APIRouter()


@router.post("/states/", response_model=CreateState)
async def create_state(state: CreateState, db: Session = Depends(get_db)):
    db_state = State(title=state.title, content=state.content, image_url=state.image_url)
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state


@router.get("/states/{state_id}", response_class=HTMLResponse)
async def read_state(
        state_id: int,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_none)
):
    state = db.query(State).filter(State.id == state_id).first()
    if state is None:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    context = {"request": request, "state": state}
    if current_user:
        context["current_user"] = current_user

    return templates.TemplateResponse("state_detail.html", context)


@router.get("/states/", response_class=HTMLResponse)
async def read_states(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_or_none)
):
    states = db.query(State).all()

    context = {"request": request, "states": states}
    if current_user:
        context["current_user"] = current_user

    return templates.TemplateResponse("states.html", context)


@router.put("/states/{state_id}", response_model=CreateState)
async def update_state(state_id: int, state: UpdateState, db: Session = Depends(get_db)):
    db_state = db.query(State).filter(State.id == state_id).first()
    if db_state is None:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    if state.title is not None:
        db_state.title = state.title
    if state.content is not None:
        db_state.content = state.content
    if state.image_url is not None:
        db_state.image_url = state.image_url

    db.commit()
    db.refresh(db_state)
    return db_state


@router.delete("/states/{states_id}")
async def delete_state(state_id: int, state: UpdateState, db: Session = Depends(get_db)):
    db_state = db.query(State).filter(State.id == state_id).first()
    if db_state is None:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    db.delete(db_state)
    db.commit()
    return {"detail": "Статья успешно удалена"}


@router.get("/states/", response_model=list[CreateState])
async def read_states(db: Session = Depends(get_db)):
    states = db.query(State).all()
    return states


@router.post("/states/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    with open(f"static/images/{file.filename}", "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": file.filename}


@router.get("/about", response_class=HTMLResponse)
async def about(
        request: Request,
        current_user: User = Depends(get_current_user_or_none)
):
    with open('static/about.txt', 'r', encoding='utf-8') as file:
        content = file.read()

    context = {"request": request, "content": content}
    if current_user:
        context["current_user"] = current_user

    return templates.TemplateResponse("about.html", context)
