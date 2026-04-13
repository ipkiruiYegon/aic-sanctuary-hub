import uuid
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, Relationship


class Region(SQLModel, table=True):
    __tablename__ = "regions"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    name: str

    # Removed Mapped[]; SQLModel handles the List hint automatically
    districts: List["District"] = Relationship(back_populates="region")


class District(SQLModel, table=True):
    __tablename__ = "districts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    region_id: uuid.UUID = Field(foreign_key="regions.id")

    region: Optional["Region"] = Relationship(back_populates="districts")
    churches: List["Church"] = Relationship(back_populates="district")


class Church(SQLModel, table=True):
    __tablename__ = "churches"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    district_id: uuid.UUID = Field(foreign_key="districts.id")

    district: Optional["District"] = Relationship(back_populates="churches")
    # Ensure back_populates matches User model
    users: List["User"] = Relationship(back_populates="local_church")


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(sa_column=Column(
        pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4))
    title: str = Field(max_length=12)
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
    rcc_role: Optional[str] = Field(default=None)
    dcc_role: Optional[str] = Field(default=None)
    lcc_role: Optional[str] = Field(default=None)
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
    local_church_id: uuid.UUID = Field(foreign_key="churches.id")
    district_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="districts.id")
    region_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="regions.id")

    local_church: Optional["Church"] = Relationship(back_populates="users")
    district: Optional["District"] = Relationship()
    region: Optional["Region"] = Relationship()


class Event(SQLModel, table=True):
    __tablename__ = "events"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_name: str
    event_type: str
    description: Optional[str] = None
    date_from: datetime
    date_to: datetime
    status: Optional[str] = Field(default="Scheduled")
    venue_church_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="churches.id")
    venue_district_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="districts.id")
    venue_region_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="regions.id")
    actual_venue: str
    target_group: str
    approved: Optional[bool] = Field(default=False)
    created_by: uuid.UUID = Field(
        foreign_key="users.id"
    )
    approved_by: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.id"
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.now, nullable=True))
    created_at: Optional[datetime] = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now, nullable=False)
    )

    creator: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Event.created_by]"}
    )
    approver: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Event.approved_by]"}
    )
    venue_church: Optional["Church"] = Relationship()
    venue_district: Optional["District"] = Relationship()
    venue_region: Optional["Region"] = Relationship()
