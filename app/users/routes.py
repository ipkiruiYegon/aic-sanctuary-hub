import uuid
from fastapi import APIRouter, Depends, status, Request, Form, Body
from fastapi.responses import HTMLResponse, JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database import get_session
from app.users.service import UserService  # Import your UserService here
# Import the CouncilService for region data
from app.council.service import CouncilService
# Import the templates object from core/templates.py
from app.core.templates import templates
# Import your Sql_models here
from app.users.models import UserCreate, userPublic, user_create_form, UserUpdate, UserStatus


user_router = APIRouter()

user_service = UserService()  # Instantiate your service
# Instantiate the CouncilService for region data
council_services = CouncilService()

LCC_ROLE_OPTIONS = [
    {"id": "LCC Chairman", "name": "LCC Chairman"},
    {"id": "LCC Vice Chairman", "name": "LCC Vice Chairman"},
    {"id": "LCC Treasurer", "name": "LCC Treasurer"},
    {"id": "LCC Secretary", "name": "LCC Secretary"},
    {"id": "LCC Vice Secretary", "name": "LCC Vice Secretary"},
    {"id": "CED leader", "name": "CED Leader"},
    {"id": "LCC Youth Leader", "name": "LCC Youth Leader"},
    {"id": "LCC Youth Secretary", "name": "LCC Youth Secretary"},
    {"id": "LCC Youth Vice Secretary", "name": "LCC Youth Vice Secretary"},
    {"id": "LCC Youth Treasurer", "name": "LCC Youth Treasurer"},
    {"id": "LCC Women Leader", "name": "LCC Women Leader"},
    {"id": "LCC Women Secretary", "name": "LCC Women Secretary"},
    {"id": "LCC Women Vice Secretary", "name": "LCC Women Vice Secretary"},
    {"id": "LCC Women Treasurer", "name": "LCC Women Treasurer"},
    {"id": "LCC Widows Leader", "name": "LCC Widows Leader"},
    {"id": "LCC Widows Secretary", "name": "LCC Widows Secretary"},
    {"id": "LCC Widows Vice Secretary", "name": "LCC Widows Vice Secretary"},
    {"id": "LCC Widows Treasurer", "name": "LCC Widows Treasurer"},
]

DCC_ROLE_OPTIONS = [
    {"id": "DCC Chairman", "name": "DCC Chairman"},
    {"id": "DCC Vice Chairman", "name": "DCC Vice Chairman"},
    {"id": "DCC Treasurer", "name": "DCC Treasurer"},
    {"id": "DCC Secretary", "name": "DCC Secretary"},
    {"id": "DCC Vice Secretary", "name": "DCC Vice Secretary"},
    {"id": "CED Worker", "name": "CED Worker"},
    {"id": "DCC Youth Leader", "name": "DCC Youth Leader"},
    {"id": "DCC Youth Secretary", "name": "DCC Youth Secretary"},
    {"id": "DCC Youth Vice Secretary", "name": "DCC Youth Vice Secretary"},
    {"id": "DCC Youth Treasurer", "name": "DCC Youth Treasurer"},
    {"id": "DCC Women Leader", "name": "DCC Women Leader"},
    {"id": "DCC Women Secretary", "name": "DCC Women Secretary"},
    {"id": "DCC Women Vice Secretary", "name": "DCC Women Vice Secretary"},
    {"id": "DCC Women Treasurer", "name": "DCC Women Treasurer"},
    {"id": "DCC Widows Leader", "name": "DCC Widows Leader"},
    {"id": "DCC Widows Secretary", "name": "DCC Widows Secretary"},
    {"id": "DCC Widows Vice Secretary", "name": "DCC Widows Vice Secretary"},
    {"id": "DCC Widows Treasurer", "name": "DCC Widows Treasurer"},
]

RCC_ROLE_OPTIONS = [
    {"id": "RCC Chairman", "name": "RCC Chairman"},
    {"id": "RCC Vice Chairman", "name": "RCC Vice Chairman"},
    {"id": "RCC Treasurer", "name": "RCC Treasurer"},
    {"id": "Administrative Secretary", "name": "Administrative Secretary"},
    {"id": "RCC Vice Secretary", "name": "RCC Vice Secretary"},
    {"id": "CED Coordinator", "name": "CED Coordinator"},
    {"id": "RCC Youth Leader", "name": "RCC Youth Leader"},
    {"id": "RCC Youth Secretary", "name": "RCC Youth Secretary"},
    {"id": "RCC Youth Vice Secretary", "name": "RCC Youth Vice Secretary"},
    {"id": "RCC Youth Treasurer", "name": "RCC Youth Treasurer"},
    {"id": "RCC Women Leader", "name": "RCC Women Leader"},
    {"id": "RCC Women Secretary", "name": "RCC Women Secretary"},
    {"id": "RCC Women Vice Secretary", "name": "RCC Women Vice Secretary"},
    {"id": "RCC Women Treasurer", "name": "RCC Women Treasurer"},
    {"id": "RCC Widows Leader", "name": "RCC Widows Leader"},
    {"id": "RCC Widows Secretary", "name": "RCC Widows Secretary"},
    {"id": "RCC Widows Vice Secretary", "name": "RCC Widows Vice Secretary"},
    {"id": "RCC Widows Treasurer", "name": "RCC Widows Treasurer"},
]


@user_router.post("/create")
async def create_user(user_data: UserCreate = Depends(user_create_form), session: AsyncSession = Depends(get_session)):
    # print(f"Received user data: {user_data}")
    if await user_service.user_phone_exists(user_data.phone_no, session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with this phone number already exists")
    user = await user_service.create_user(user_data, session)
    return JSONResponse(content={"success": True, "user_id": str(user.id)}, status_code=status.HTTP_201_CREATED)


@user_router.get("", response_class=HTMLResponse)
async def get_users(request: Request, session: AsyncSession = Depends(get_session)):
    # Query users from DB
    users = await user_service.get_all_users(session)
    region = await council_services.get_region_with_hierarchy(session)
    region_exists = region is not None
    # Render Jinja template instead of returning JSON
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": users,
            "region": region, "region_exists": region_exists, "roles": LCC_ROLE_OPTIONS, "dcc_roles": DCC_ROLE_OPTIONS, "rcc_roles": RCC_ROLE_OPTIONS}
    )


@user_router.get("/table", response_class=HTMLResponse)
async def users_table(request: Request, session: AsyncSession = Depends(get_session)):
    users = await user_service.get_all_users(session)
    region = await council_services.get_region_with_hierarchy(session)
    region_exists = region is not None
    return templates.TemplateResponse("users_table.html", {
        "request": request,
        "users": users,
        "region": region,
        "region_exists": region_exists
    })


@user_router.get("/{user_id}", response_model=userPublic)
async def get_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    # Example raw query; adjust based on your schema
    user = await user_service.get_user_by_uid(user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return user


@user_router.post("/update")
async def update_user(user_data: UserUpdate, session: AsyncSession = Depends(get_session)):
    # Example raw query; adjust based on your schema
    if not await user_service.user_exists(user_data.id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    if await user_service.update_user(user_data.model_dump(exclude_none=True), session):
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True, "message": "User updated successfully"})
    else:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"success": False, "message": "No changes detected"})


# delete user route that does not delete but sets is_active to false


@user_router.post("/update/status")
async def update_user_status(user_status_data: UserStatus, session: AsyncSession = Depends(get_session)):
    user_id = user_status_data.user_id
    user = await user_service.get_user_by_uid(user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    user_updated = await user_service.update_user_status(user_status_data.user_id, user_status_data.reason, session)
    if not user_updated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Failed to update user status")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True, "message": "User status updated successfully"})
