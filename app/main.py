from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
import asyncpg
from fastapi.templating import Jinja2Templates

from config import settings  # Import settings from config
from .routes import users  # Import the users router

DATABASE_URL = settings.database_url
templates = Jinja2Templates(directory="./templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create connection pool
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)
    yield
    # Shutdown: Close pool
    await app.state.pool.close()

app = FastAPI(title="AIC Sanctuary Hub", description="A centralized digital platform for AIC church officials", lifespan=lifespan)

async def get_db():
    async with app.state.pool.acquire() as connection:
        yield connection


# Include routers
#app.include_router(users.router)

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})