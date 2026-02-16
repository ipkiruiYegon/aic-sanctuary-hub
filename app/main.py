from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from .routes import users  # Import the users router


templates = Jinja2Templates(directory="./templates")


app = FastAPI()
# Include routers
app.include_router(users.router)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
