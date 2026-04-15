from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import JSONResponse
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


@events_router.post("/create")
async def events(request: Request, event_data: EventSchema, session: AsyncSession = Depends(get_session)):
    current_user = request.state.user["user"]["user_id"]
    print("user", current_user)
    event = await event_services.create_event(current_user, event_data, session)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"success": True, "message": "User status updated successfully"})
