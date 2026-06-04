import uuid
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime


if TYPE_CHECKING:
    from app.users.models import User
    from app.council.models import Church, District, Region
    from app.notifications.models import EventLike, EventComment


class EventBase(SQLModel):
    event_name: str
    event_type: str
    date_from: datetime
    date_to: datetime
    actual_venue: Optional[str]
    target_group: str


class EventSchema(EventBase):
    venue_church_id: Optional[uuid.UUID]
    venue_district_id: Optional[uuid.UUID]
    venue_region_id: uuid.UUID
    event_programmer: Optional[str] = None
    event_speaker: Optional[str] = None


class EventPublic(EventSchema):
    pass


class Event(EventBase, table=True):
    __tablename__ = "events"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    description: Optional[str] = None
    status: Optional[str] = Field(default="Scheduled")
    venue_church_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="churches.id")
    venue_district_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="districts.id")
    venue_region_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="regions.id")
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
        sa_relationship_kwargs={
            "foreign_keys": "[Event.created_by]", "lazy": "selectin"}
    )
    approver: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Event.approved_by]", "lazy": "selectin"}
    )
    venue_church: Optional["Church"] = Relationship()
    venue_district: Optional["District"] = Relationship()
    venue_region: Optional["Region"] = Relationship()
    event_programmer: Optional[str] = None
    event_speaker: Optional[str] = None

    # Notification relationships
    likes: list["EventLike"] = Relationship(back_populates="event")
    comments: list["EventComment"] = Relationship(back_populates="event")
