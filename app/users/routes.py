from fastapi import APIRouter, Depends, status
from fastapi.responses import HTMLResponse
from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database import get_session
from app.users.service import UserService  # Import your UserService here
# Import the templates object from core/templates.py
from app.core.templates import templates
# Import your Pydantic schemas here
from app.users.schemas import UserBaseModel, UserCreateModel, UserUpdateModel

user_router = APIRouter()

user_service = UserService()  # Instantiate your service


@user_router.post("/")
async def create_user(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    user_phone = user_data.phone_no
    if await user_service.user_exists(user_phone, session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with this phone number already exists")
    user = await user_service.create_user(user_data, session)
    return user


@user_router.get("/", response_class=HTMLResponse)
async def get_users(request: Request, session: AsyncSession = Depends(get_session)):
    # Query users from DB
    users = await user_service.get_all_users(session)
    # Render Jinja template instead of returning JSON
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": users}
    )


@user_router.get("/{user_id}", response_model=UserBaseModel)
async def get_user(user_id: str, session: AsyncSession = Depends(get_session)):
    # Example raw query; adjust based on your schema
    user = await user_service.get_user_by_uid(user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return user
