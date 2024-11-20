from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from renova.db import init_db
from renova.routers import admin, therapists
from renova.templates import templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(admin.router, prefix="/admin")
app.include_router(therapists.router)


@app.get("/")
def get_root(request: Request):
    return templates.TemplateResponse(request, "index.html")
