import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.events.models import EventSchema
from app.events.models import Event
from app.users.models import User


class EventService:
    async def create_event(self, current_user, event_data: EventSchema, session: AsyncSession):
        # Logic to create a new event in the database
        new_event = Event(**event_data.model_dump())
        new_event.event_name = event_data.event_name.title()
        new_event.actual_venue = event_data.actual_venue.title()
        new_event.target_group = event_data.target_group.title()
        new_event.created_by = current_user

        session.add(new_event)
        await session.commit()
        await session.refresh(new_event)
        return new_event

    async def get_approved_events(self, session: AsyncSession):
        sql = select(Event).where(Event.approved == True)
        results = await session.exec(sql)
        events = results.all()
        return events

    async def get_unapproved_events(self, session: AsyncSession):
        sql = select(Event).where(Event.approved == False, Event.status != "Rejected").options(
            selectinload(Event.creator)
            # ONLY load these
            .load_only(User.first_name, User.last_name, User.role)
        )
        results = await session.exec(sql)
        events = results.all()
        return events

    async def approve_event(self, event_id: uuid.UUID, approver_id: uuid.UUID, update_data: dict, session: AsyncSession):
        sql = select(Event).where(Event.id == event_id)
        result = await session.exec(sql)
        event = result.one_or_none()

        if not event:
            return None

        if str(event.created_by) == str(approver_id):
            raise ValueError("You cannot approve your own event")

        event.event_name = update_data.get("event_name", event.event_name)
        event.event_type = update_data.get("event_type", event.event_type)
        event.date_from = update_data.get("date_from", event.date_from)
        event.date_to = update_data.get("date_to", event.date_to)
        event.venue_region_id = update_data.get(
            "venue_region_id", event.venue_region_id)
        event.venue_district_id = update_data.get(
            "venue_district_id", event.venue_district_id)
        event.venue_church_id = update_data.get(
            "venue_church_id", event.venue_church_id)
        event.actual_venue = update_data.get(
            "actual_venue", event.actual_venue)
        event.target_group = update_data.get(
            "target_group", event.target_group)
        event.description = update_data.get("description", event.description)
        event.approved = True
        event.approved_by = approver_id
        event.status = "Approved"

        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event

    async def reject_event(self, event_id: uuid.UUID, reject_reason: str, session: AsyncSession):
        sql = select(Event).where(Event.id == event_id)
        result = await session.exec(sql)
        event = result.one_or_none()

        if not event:
            return None

        event.approved = False
        event.approved_by = None
        event.status = "Rejected"
        event.description = reject_reason

        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event

    async def get_upcoming_events(self, session: AsyncSession, current_time: datetime = None, limit: int = 50):
        if current_time is None:
            current_time = datetime.now()
        sql = select(Event).where(
            Event.approved == True,
            Event.date_from >= current_time,
            Event.status != "Cancelled"
        ).order_by(Event.date_from).limit(limit)
        results = await session.exec(sql)
        events = results.all()
        return events

    async def get_past_events(self, session: AsyncSession, current_time: datetime = None, limit: int = 50):
        if current_time is None:
            current_time = datetime.now()
        sql = select(Event).where(
            Event.approved == True,
            Event.date_to < current_time,
            Event.status != "Cancelled"
        ).order_by(Event.date_to.desc()).limit(limit)
        results = await session.exec(sql)
        events = results.all()
        return events
