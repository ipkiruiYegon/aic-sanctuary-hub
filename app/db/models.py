import uuid
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, date
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(sa_column=Column(
        pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4))
    first_name: str = Field(max_length=12)
    last_name: str = Field(max_length=50)
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
    role: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now, nullable=False)
    )
    created_by: Optional[str] = Field(default="Admin")
    updated_by: Optional[str] = Field(default=None)
    phone_no: str = Field(max_length=10, unique=True, regex=r"^0\d{9}$")
    avatar_image: Optional[str] = Field(default=None)
    linked: Optional[bool] = Field(default=False)
    updated_at: Optional[datetime] = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.now, nullable=True))
    mobile_login: Optional[bool] = Field(default=False)
    last_login_mobile: Optional[datetime] = Field(default=None, nullable=True)
