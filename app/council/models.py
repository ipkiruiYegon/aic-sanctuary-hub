import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.users.models import User


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
