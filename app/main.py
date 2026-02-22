from fastapi import FastAPI, Request, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.staticfiles import StaticFiles

from .users.routes import user_router  # Import the users router
from .council.routes import council_router  # Import the council router
from .core.templates import templates  # Import the templates object
from app.db.database import get_session  # Import the async session dependency


version = "v1"

version_prefix = f"/api/{version}"

app = FastAPI(title="AIC Sanctuary Hub API",
              version=version,
              openapi_url=f"{version_prefix}/openapi.json",
              docs_url=f"{version_prefix}/docs",
              redoc_url=f"{version_prefix}/redoc"
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
