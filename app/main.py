from datetime import datetime
from email.utils import format_datetime

from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlmodel import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .users.routes import user_router  # Import the users router
from .council.routes import council_router  # Import the council router
from .auth.routes import auth_router      # Import the auth routes
from .events.routes import events_router
from .core.templates import templates  # Import the templates object
from app.db.database import get_session  # Import the async session dependency
from app.db.database import async_session
from app.council.service import CouncilService  # Import the CouncilService
from app.config import settings  # Import settings for configuration
from app.auth.utils import decode_token, get_request_token
from app.users.service import UserService

council_services = CouncilService()  # Initialize the CouncilService
version = "v1"


user_services = UserService()

version_prefix = f"/api/{version}"


def format_datetime(value, fmt="%A %d %Y, %I:%M %p"):
    return value.strftime(fmt)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session() as session:
        region = await council_services.get_region(session)
        templates.env.globals["region"] = region
        # Register globals and filters once
        templates.env.globals["current_time"] = datetime.now
        templates.env.filters["format_datetime"] = format_datetime
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


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Public routes that don't require authentication
    public_paths = ["/login", "/api/v1/auth/authenticate", "/static"]

    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)

    token = get_request_token(request)

    if not token:
        return RedirectResponse(url="/login")

    try:
        token_data = decode_token(token)
        if not token_data:
            return RedirectResponse(url="/login")

        # Verify token against DB
        async with async_session() as session:
            if not await user_services.token_in_user_db(token_data["user"]["user_id"], token, session):
                return RedirectResponse(url="/login")

        # Attach user info to request.state
        request.state.user = token_data

        # Role-based access control
        user_role = token_data.get("user", {}).get("role")
        # add user routes
        ALlOWED_USER_ROLES = {"system administrator",
                              "ced leader", "lcc treasurer", "ced worker", "ced coordinator"}
        if request.url.path.startswith("/users"):
            if user_role.lower() not in ALlOWED_USER_ROLES:
                return RedirectResponse(url="/unauthorized")

    except Exception as e:
        print("error", e)
        return RedirectResponse(url="/login")

    return await call_next(request)

# Include routers
app.include_router(
    user_router, prefix="/users", tags=["users"])
app.include_router(
    council_router, prefix="/council", tags=["council"])
app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
app.include_router(events_router, prefix="/events", tags=["events"])


@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/dashboard")
async def dashboard(request: Request, session: AsyncSession = Depends(get_session)):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/login")
async def login_page(request: Request, session: AsyncSession = Depends(get_session)):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/password/change")
async def login_page(request: Request, session: AsyncSession = Depends(get_session)):
    return templates.TemplateResponse("password_change.html", {"request": request})


@app.get("/unauthorized")
async def unauthorized(request: Request):
    return templates.TemplateResponse("unauthorized.html", {"request": request})


@app.get("/notifications")
async def notification(request: Request):
    return templates.TemplateResponse(
        "notifications.html", {"request": request})
