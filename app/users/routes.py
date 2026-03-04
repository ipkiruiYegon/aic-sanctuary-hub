import uuid
from fastapi import APIRouter, Depends, status, Request, Form
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
# Import your Pydantic schemas here
from app.users.schemas import UserCreateModel, UserBaseModel, as_form, UserUpdateModel


user_router = APIRouter()

user_service = UserService()  # Instantiate your service
# Instantiate the CouncilService for region data
council_services = CouncilService()

LCC_ROLE_OPTIONS = [
    {"id": "Chairman", "name": "Chairman"},
    {"id": "Vice Chairman", "name": "Vice Chairman"},
    {"id": "Treasurer", "name": "Treasurer"},
    {"id": "Secretary", "name": "Secretary"},
    {"id": "Vice Secretary", "name": "Vice Secretary"},
    {"id": "CED leader", "name": "CED Leader"},
    {"id": "Youth Leader", "name": "Youth Leader"},
    {"id": "Youth Secretary", "name": "Youth Secretary"},
    {"id": "Youth Vice Secretary", "name": "Youth Vice Secretary"},
    {"id": "Youth Treasurer", "name": "Youth Treasurer"},
    {"id": "Women Leader", "name": "Women Leader"},
    {"id": "Women Secretary", "name": "Women Secretary"},
    {"id": "Women Vice Secretary", "name": "Women Vice Secretary"},
    {"id": "Women Treasurer", "name": "Women Treasurer"},
    {"id": "Widows Leader", "name": "Widows Leader"},
    {"id": "Widows Secretary", "name": "Widows Secretary"},
    {"id": "Widows Vice Secretary", "name": "Widows Vice Secretary"},
    {"id": "Widows Treasurer", "name": "Widows Treasurer"},
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
async def create_user(user_data: UserCreateModel = Depends(as_form), session: AsyncSession = Depends(get_session)):
    # print(f"Received user data: {user_data}")
    if await user_service.user_phone_exists(user_data.phone_no, session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with this phone number already exists")
    user = await user_service.create_user(user_data, session)
    return JSONResponse({"success": True, "user_id": str(user.id)})


@user_router.get("/", response_class=HTMLResponse)
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


@user_router.get("/{user_id}", response_model=UserBaseModel)
async def get_user(user_id: str, session: AsyncSession = Depends(get_session)):
    # Example raw query; adjust based on your schema
    user = await user_service.get_user_by_uid(user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return user


@user_router.post("/update")
async def update_user(user_data: UserUpdateModel, session: AsyncSession = Depends(get_session)):
    # Example raw query; adjust based on your schema
    if not await user_service.user_exists(user_data.user_id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    return await user_service.update_user(user_data.model_dump(exclude_none=True), session)


# delete user route that does not delete but sets is_active to false


@user_router.delete("/update/status/{user_id}")
async def delete_user(user_id: str, session: AsyncSession = Depends(get_session)):
    user = await user_service.get_user_by_uid(user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    await user_service.delete_user(user_id, session)
    return JSONResponse({"message": "User deactivated successfully"})
