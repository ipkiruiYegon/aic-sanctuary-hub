import uuid
import re
import sqlalchemy.dialects.postgresql as pg
from pydantic import field_validator
from datetime import datetime
from typing import Optional
from fastapi import Form, HTTPException
from sqlmodel import Relationship, Field, SQLModel, Column

from app.council.models import Church, Region, District


class UserBase(SQLModel):
    title: str = Field(max_length=12)
    first_name: str = Field(max_length=12)
    last_name: str = Field(max_length=50)
    role: Optional[str] = Field(default=None)


class UserCreate(UserBase):
    phone_no: str = Field(max_length=10, unique=True, regex=r"^0\d{9}$")
    region_id: uuid.UUID = Field(..., description="Region UUID")
    district_id: uuid.UUID = Field(..., description="District UUID")
    local_church_id: uuid.UUID = Field(..., description="Church UUID")

    @field_validator("phone_no")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^0\d{9}$", v):
            raise ValueError(
                "Phone number must start with 0 and be exactly 10 digits")
        return v


class userPublic(UserBase):
    id: uuid.UUID
    rcc_role: Optional[str] = Field(default=None)
    dcc_role: Optional[str] = Field(default=None)
    lcc_role: Optional[str] = Field(default=None)
    phone_no: str
    avatar_image: Optional[str]
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    is_staff: Optional[bool]


def user_create_form(
    title: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_no: str = Form(...),
    role: str = Form(...),
    region_id: str = Form(...),
    district_id: str = Form(...),
    local_church_id: str = Form(...),
) -> UserCreate:
    try:
        return UserCreate(
            title=title,
            first_name=first_name,
            last_name=last_name,
            phone_no=phone_no,
            role=role,
            region_id=region_id,
            district_id=district_id,
            local_church_id=local_church_id,
        )
    except ValueError as e:
        # This catches your @field_validator errors and returns them to the UI
        raise HTTPException(status_code=422, detail=str(e))


class UserUpdate(UserCreate):
    id: uuid.UUID = Field(..., description="User UUID")
    phone_no: str = Field(max_length=10, unique=True, regex=r"^0\d{9}$")
    region_id: uuid.UUID = Field(..., description="Region UUID")
    district_id: uuid.UUID = Field(..., description="District UUID")
    local_church_id: uuid.UUID = Field(..., description="Church UUID")

    @field_validator("phone_no")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^0\d{9}$", v):
            raise ValueError(
                "Phone number must start with 0 and be exactly 10 digits")
        return v


class UserStatus(SQLModel):
    user_id: uuid.UUID
    reason: Optional[str]


class User(UserBase, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(sa_column=Column(
        pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4))
    is_active: Optional[bool] = Field(default=False)
    is_superuser: Optional[bool] = Field(default=False)
    is_staff: Optional[bool] = Field(default=False)
    password_hash: str = Field(sa_column=Column(
        pg.VARCHAR, nullable=False), exclude=True)
    last_login: Optional[datetime] = Field(default=None)
    reset_password: Optional[bool] = Field(default=None)
    password_status: Optional[str] = Field(default="Change")
    login_attempts: Optional[int] = Field(default=0)
    mobile_login_attempts: Optional[int] = Field(default=0)
    token: Optional[str] = Field(default=None)
    reset_token: Optional[str] = Field(default=None)
    rcc_role: Optional[str] = Field(default=None)
    dcc_role: Optional[str] = Field(default=None)
    lcc_role: Optional[str] = Field(default=None)
    phone_no: str = Field(max_length=10, unique=True, regex=r"^0\d{9}$")
    created_at: Optional[datetime] = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now, nullable=False)
    )
    created_by: Optional[str] = Field(default="Admin")
    updated_by: Optional[str] = Field(default=None)
    avatar_image: Optional[str] = Field(default=None)
    linked: Optional[bool] = Field(default=False)
    updated_at: Optional[datetime] = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.now, nullable=True))
    mobile_login: Optional[bool] = Field(default=False)
    last_login_mobile: Optional[datetime] = Field(default=None, nullable=True)
    local_church_id: uuid.UUID = Field(foreign_key="churches.id")
    district_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="districts.id")
    region_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="regions.id")

    local_church: Optional["Church"] = Relationship(back_populates="users")
    district: Optional["District"] = Relationship()
    region: Optional["Region"] = Relationship()
