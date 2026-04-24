import uuid
from sqlmodel import SQLModel, Field, Column, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
from enum import Enum

if TYPE_CHECKING:
    from app.events.models import Event
    from app.users.models import User


class NotificationType(str, Enum):
    EVENT_CREATED = "event_created"
    EVENT_UPDATED = "event_updated"
    EVENT_CANCELLED = "event_cancelled"
    EVENT_LIKED = "event_liked"
    EVENT_COMMENTED = "event_commented"
    USER_JOINED = "user_joined"
    SYSTEM_ANNOUNCEMENT = "system_announcement"
    PROFILE_UPDATED = "profile_updated"


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    type: NotificationType
    title: str
    message: str
    # ID of related object (event, user, etc.)
    related_id: Optional[uuid.UUID] = None
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    user: "User" = Relationship(back_populates="notifications")


class NotificationPreference(SQLModel, table=True):
    __tablename__ = "notification_preferences"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    event_created: bool = Field(default=True)
    event_updated: bool = Field(default=True)
    event_cancelled: bool = Field(default=True)
    event_liked: bool = Field(default=False)
    event_commented: bool = Field(default=True)
    user_joined: bool = Field(default=False)
    system_announcements: bool = Field(default=True)
    profile_updates: bool = Field(default=False)
    email_notifications: bool = Field(default=True)
    push_notifications: bool = Field(default=True)

    # Relationships
    user: "User" = Relationship(back_populates="notification_preferences")


class EventLike(SQLModel, table=True):
    __tablename__ = "event_likes"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: uuid.UUID = Field(foreign_key="events.id")
    user_id: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    event: "Event" = Relationship(back_populates="likes")
    user: "User" = Relationship(back_populates="event_likes")


class EventComment(SQLModel, table=True):
    __tablename__ = "event_comments"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_id: uuid.UUID = Field(foreign_key="events.id")
    user_id: uuid.UUID = Field(foreign_key="users.id")
    comment: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    # Relationships
    event: "Event" = Relationship(back_populates="comments")
    user: "User" = Relationship(back_populates="event_comments")
