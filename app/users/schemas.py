import uuid
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from fastapi import Form


class UserCreateSchema(BaseModel):
    title: str
    first_name: str
    last_name: str
    phone_no: str
    role: str
    region_id: uuid.UUID = Field(..., description="Region UUID")
    district_id: uuid.UUID = Field(..., description="District UUID")
    local_church_id: uuid.UUID = Field(..., description="Church UUID")

    @validator("phone_no")
    def validate_phone(cls, v):
        if not v.isdigit():
            raise ValueError("Phone number must contain only digits")
        if len(v) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        if not v.startswith("0"):
            raise ValueError("Phone number must begin with 0")
        return v


def as_form(
    title: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_no: str = Form(...),
    role: str = Form(...),
    region_id: str = Form(...),
    district_id: str = Form(...),
    local_church_id: str = Form(...),
) -> UserCreateSchema:
    return UserCreateSchema(
        title=title,
        first_name=first_name,
        last_name=last_name,
        phone_no=phone_no,
        role=role,
        region_id=region_id,
        district_id=district_id,
        local_church_id=local_church_id,
    )


class UserEditSchema(BaseModel):
    id: uuid.UUID = Field(..., description="User UUID")
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    role: Optional[str]


class UserSchema(BaseModel):
    id: uuid.UUID
    title: str
    first_name: str
    last_name: str
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    is_staff: Optional[bool]
    password_hash: str = Field(exclude=True)
    last_login: Optional[datetime]
    reset_password: Optional[bool]
    password_status: Optional[str]
    login_attempts: Optional[int]
    mobile_login_attempts: Optional[int]
    token: Optional[str] = Field(default=None)
    reset_token: Optional[str] = Field(default=None)
    role: Optional[str] = Field(default=None)
    rcc_role: Optional[str] = Field(default=None)
    dcc_role: Optional[str] = Field(default=None)
    lcc_role: Optional[str] = Field(default=None)
    phone_no: str
    avatar_image: Optional[str]
    linked: Optional[bool]
    updated_at: Optional[datetime]
    mobile_login: Optional[bool]
    last_login_mobile: Optional[datetime]


class UserUpdateSchema(BaseModel):
    user_id: uuid.UUID
    title: str
    first_name: str
    last_name: Optional[str]
    phone_no: Optional[str]
    rcc_role: Optional[str]
    dcc_role: Optional[str]
    lcc_role: Optional[str]
    region_id: uuid.UUID
    district_id: uuid.UUID
    local_church_id: uuid.UUID


class UserStatusSchema(BaseModel):
    user_id: uuid.UUID
    reason: Optional[str]
