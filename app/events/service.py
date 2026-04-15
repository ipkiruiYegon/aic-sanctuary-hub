from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload

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
        sql = select(Event).where(Event.approved == False).options(
            selectinload(Event.creator)
            # ONLY load these
            .load_only(User.first_name, User.last_name, User.role)
        )
        results = await session.exec(sql)
        events = results.all()
        return events
