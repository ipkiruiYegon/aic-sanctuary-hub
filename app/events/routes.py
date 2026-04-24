from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.templates import templates
from app.db.database import get_session
from app.council.service import CouncilService
from app.events.models import EventSchema
from app.events.service import EventService

events_router = APIRouter()


# Instantiate the Services
council_services = CouncilService()
event_services = EventService()


@events_router.get("")
async def events(request: Request, session: AsyncSession = Depends(get_session)):
    region = await council_services.get_region_with_hierarchy(session)
    unapproved_events = await event_services.get_unapproved_events(session)
    current_user = request.state.user["user"]

    return templates.TemplateResponse("events.html", {"request": request, "region": region, "pending_events": unapproved_events, "current_user": current_user})


@events_router.post("/{event_id}/approve")
async def approve_event(
    request: Request,
    event_id: UUID,
    event_name: str = Form(...),
    event_type: str = Form(...),
    date_from: datetime = Form(...),
    date_to: datetime = Form(...),
    venue_region_id: UUID = Form(...),
    venue_district_id: UUID = Form(...),
    venue_church_id: UUID = Form(...),
    actual_venue: str = Form(...),
    target_group: str = Form(...),
    description: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
):
    current_user = request.state.user["user"]["user_id"]

    try:
        await event_services.approve_event(
            event_id,
            current_user,
            {
                "event_name": event_name,
                "event_type": event_type,
                "date_from": date_from,
                "date_to": date_to,
                "venue_region_id": venue_region_id,
                "venue_district_id": venue_district_id,
                "venue_church_id": venue_church_id,
                "actual_venue": actual_venue,
                "target_group": target_group,
                "description": description,
            },
            session,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))

    return RedirectResponse(url="/events", status_code=status.HTTP_303_SEE_OTHER)


@events_router.post("/{event_id}/reject")
async def reject_event(
    event_id: UUID,
    description: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    await event_services.reject_event(event_id, description, session)
    return RedirectResponse(url="/events", status_code=status.HTTP_303_SEE_OTHER)


@events_router.post("/create")
async def events(request: Request, event_data: EventSchema, session: AsyncSession = Depends(get_session)):
    current_user = request.state.user["user"]["user_id"]

    event = await event_services.create_event(current_user, event_data, session)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"success": True, "message": "Event created successfully", "event": str(event.id)})
