
import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserCreateModel(BaseModel):
    title: str
    first_name: str
    last_name: str
    phone_no: str
    role: str
    region_id: uuid.UUID = Field(..., description="Region UUID")
    district_id: uuid.UUID = Field(..., description="District UUID")
    church_id: uuid.UUID = Field(..., description="Church UUID")


class UserEditSchema(BaseModel):
    id: uuid.UUID = Field(..., description="User UUID")
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    role: Optional[str]


class UserBaseModel(BaseModel):
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


class UserUpdateModel(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str]
    role: Optional[str]
    phone_no: Optional[str]
