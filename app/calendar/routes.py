from datetime import date
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
import holidays

from app.core.templates import templates
from app.db.database import get_session
from app.events.service import EventService

calendar_router = APIRouter()

calendar_service = EventService()


@calendar_router.get("")
async def calendar_page(request: Request, session: AsyncSession = Depends(get_session)):
    return templates.TemplateResponse("calendar.html", {"request": request})


@calendar_router.get("/api/month")
async def calendar_month_api(
    year: int = Query(..., ge=1900),
    month: int = Query(..., ge=1, le=12),
    session: AsyncSession = Depends(get_session)
):
    try:
        event_list = await calendar_service.get_events_for_month(session, year, month)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    country_holidays = holidays.CountryHoliday("KE", years=[year])
    holidays_list = []
    for holiday_date, name in country_holidays.items():
        if holiday_date.month == month:
            holidays_list.append({
                "date": holiday_date.isoformat(),
                "name": name
            })

    events = []
    for event in event_list:
        events.append({
            "id": str(event.id),
            "event_name": event.event_name,
            "event_type": event.event_type,
            "date_from": event.date_from.isoformat(),
            "date_to": event.date_to.isoformat(),
            "actual_venue": event.actual_venue,
            "target_group": event.target_group,
            "description": event.description or ""
        })

    return {
        "events": events,
        "holidays": holidays_list
    }
