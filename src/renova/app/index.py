from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, PackageLoader

from renova.app import therapists
from renova.db import init_db

templates = Jinja2Templates(env=Environment(loader=PackageLoader("renova")))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(therapists.router)


@app.get("/")
def get_root(request: Request):
    return templates.TemplateResponse(request, "index.html")
