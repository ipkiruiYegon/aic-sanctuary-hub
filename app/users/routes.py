import uuid
from fastapi import APIRouter, Depends, status, Request, Form
from fastapi.responses import HTMLResponse
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
from app.users.schemas import UserCreateModel, UserBaseModel

user_router = APIRouter()

user_service = UserService()  # Instantiate your service
# Instantiate the CouncilService for region data
council_services = CouncilService()

ROLE_OPTIONS = [
    {"id": "chairman", "name": "Chairman"},
    {"id": "treasurer", "name": "Treasurer"},
    {"id": "secretary", "name": "Secretary"},
    {"id": "vice_secretary", "name": "Vice Secretary"},
    {"id": "ced_leader", "name": "CED Leader"},
    {"id": "youth_leader", "name": "Youth Leader"},
    {"id": "youth_secretary", "name": "Youth Secretary"},
    {"id": "youth_vice_secretary", "name": "Youth Vice Secretary"},
    {"id": "youth_treasurer", "name": "Youth Treasurer"},
    {"id": "women_leader", "name": "Women Leader"},
    {"id": "women_secretary", "name": "Women Secretary"},
    {"id": "women_vice_secretary", "name": "Women Vice Secretary"},
    {"id": "women_treasurer", "name": "Women Treasurer"},
    {"id": "widows_leader", "name": "Widows Leader"},
    {"id": "widows_secretary", "name": "Widows Secretary"},
    {"id": "widows_vice_secretary", "name": "Widows Vice Secretary"},
    {"id": "widows_treasurer", "name": "Widows Treasurer"},
]


@user_router.post("/create")
async def create_user(title: str = Form(...),
                      first_name: str = Form(...),
                      last_name: str = Form(...),
                      phone_no: str = Form(...),
                      role: str = Form(...),
                      region_id: uuid.UUID = Form(...),
                      district_id: uuid.UUID = Form(...),
                      church_id: uuid.UUID = Form(...), session: AsyncSession = Depends(get_session)):
    user_data = {
        "title": title,
        "first_name": first_name,
        "last_name": last_name,
        "phone_no": phone_no,
        "role": role,
        "region_id": region_id,
        "district_id": district_id,
        "local_church_id": church_id,
    }

    if await user_service.user_exists(phone_no, session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with this phone number already exists")
    user = await user_service.create_user(user_data, session)
    return RedirectResponse(url="/users", status_code=303)


@user_router.get("/", response_class=HTMLResponse)
async def get_users(request: Request, session: AsyncSession = Depends(get_session)):
    # Query users from DB
    users = await user_service.get_all_users(session)
    region = await council_services.get_region_with_hierarchy(session)
    region_exists = region is not None
    # Render Jinja template instead of returning JSON
    print(f"Region data for template: {region}")
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": users,
            "region": region, "region_exists": region_exists, "roles": ROLE_OPTIONS}
    )


@user_router.get("/{user_id}", response_model=UserBaseModel)
async def get_user(user_id: str, session: AsyncSession = Depends(get_session)):
    # Example raw query; adjust based on your schema
    user = await user_service.get_user_by_uid(user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return user
