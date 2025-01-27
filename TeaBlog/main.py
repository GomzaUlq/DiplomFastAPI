from fastapi import FastAPI
from routes import user, state, catalog, cart
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user.router)
app.include_router(state.router)
app.include_router(catalog.router)
app.include_router(cart.router, prefix="/cart")

