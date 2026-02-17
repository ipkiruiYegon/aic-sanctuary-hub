from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from .users.routes import user_router  # Import the users router


templates = Jinja2Templates(directory="app/templates")

version = "v1"

version_prefix = f"/api/{version}"

app = FastAPI(title="AIC Sanctuary Hub API",
              version=version,
              openapi_url=f"{version_prefix}/openapi.json",
              docs_url=f"{version_prefix}/docs",
              redoc_url=f"{version_prefix}/redoc"
              )
# Include routers
app.include_router(
    user_router, prefix=f"{version_prefix}/users", tags=["users"])


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
