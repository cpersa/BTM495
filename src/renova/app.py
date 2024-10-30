from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from renova.db import init_db
from renova.routers import admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("asdf")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(admin.router)


@app.get("/")
def read_root():
    html_content = """
        <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <script src="https://cdn.tailwindcss.com"></script>
                <script src="https://unpkg.com/htmx.org@2.0.2" integrity="sha384-Y7hw+L/jvKeWIRRkqWYfPcvVxHzVzn5REgzbawhxAuQGwX1XWe70vji+VSeHOThJ" crossorigin="anonymous"></script>            
            </head>
            <body>
                <h1 class="text-3xl font-bold underline">
                    Hello world!
                </h1>
            </body>
        </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
