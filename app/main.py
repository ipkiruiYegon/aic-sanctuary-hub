from fastapi import FastAPI, Request, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlmodel import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .users.routes import user_router  # Import the users router
from .council.routes import council_router  # Import the council router
from .core.templates import templates  # Import the templates object
from app.db.database import get_session  # Import the async session dependency
from app.council.service import CouncilService  # Import the CouncilService
from app.config import settings  # Import settings for configuration

council_services = CouncilService()  # Initialize the CouncilService
version = "v1"

DATABASE_URL = settings.DATABASE_URL

async_engine = create_async_engine(url=DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

version_prefix = f"/api/{version}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session() as session:
        region = await council_services.get_region(session)
        templates.env.globals["region"] = region
    yield
    print("Application is shutting down...")

app = FastAPI(title="AIC Sanctuary Hub API",
              version=version,
              openapi_url=f"{version_prefix}/openapi.json",
              docs_url=f"{version_prefix}/docs",
              redoc_url=f"{version_prefix}/redoc",
              lifespan=lifespan
              )

app.mount("/static", StaticFiles(directory="app/static"), name="static")
# Include routers
app.include_router(
    user_router, prefix="/users", tags=["users"])
app.include_router(
    council_router, prefix="/council", tags=["council"])


@app.get("/")
async def home(request: Request, session: AsyncSession = Depends(get_session)):

    return templates.TemplateResponse("dashboard.html", {"request": request})
