import uuid
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import Session, select
from app.db.database import get_session
from app.council.service import CouncilService
from app.council.models import Church, District, Region
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List

# Import the templates object from core/templates.py
from app.core.templates import templates
council_router = APIRouter()
council_services = CouncilService()  # Instantiate the service


# ==================== API Endpoints for Budget ====================

@council_router.get("/api/churches", response_model=List[dict])
async def get_all_churches_api(request: Request, session: AsyncSession = Depends(get_session)):
    """Get all churches as JSON for budget allocation"""
    statement = select(Church)
    result = await session.exec(statement)
    churches = result.all()
    return [{"id": str(church.id), "name": church.name, "district_id": str(church.district_id)} for church in churches]


@council_router.get("/api/churches/{district_id}/local", response_model=List[dict])
async def get_local_churches_api(district_id: uuid.UUID, request: Request, session: AsyncSession = Depends(get_session)):
    """Get all local churches for a specific district"""
    statement = select(Church).where(Church.district_id == district_id)
    result = await session.exec(statement)
    churches = result.all()
    return [{"id": str(church.id), "name": church.name} for church in churches]


@council_router.get("/api/regions", response_model=List[dict])
async def get_regions_api(request: Request, session: AsyncSession = Depends(get_session)):
    """Get all regions"""
    statement = select(Region)
    result = await session.exec(statement)
    regions = result.all()
    return [{"id": str(region.id), "name": region.name} for region in regions]


@council_router.get("/api/churches/dcc/{dcc_id}/local", response_model=List[dict])
async def get_local_churches_for_dcc_api(dcc_id: uuid.UUID, request: Request, session: AsyncSession = Depends(get_session)):
    """Get local churches for a specific DCC by matching district."""
    church = await session.get(Church, dcc_id)
    if church is None:
        return []
    statement = select(Church).where(Church.district_id ==
                                     church.district_id, Church.id != dcc_id)
    result = await session.exec(statement)
    churches = result.all()
    return [{"id": str(church.id), "name": church.name} for church in churches]


# ==================== HTML Routes ====


@council_router.get("/get-churches", response_class=HTMLResponse)
async def get_churches(request: Request, session: AsyncSession = Depends(get_session)):
    # Find the specific district from your 'region' object
    # (Assuming 'region' is available or fetched from DB)
    params = dict(request.query_params)

    district_id = next((v for k, v in params.items()
                       if "district" in k), None)
    if not district_id:
        return None
    print(district_id)
    selected_district = await council_services.get_churches_by_district(
        uuid.UUID(district_id), session)

    options = '<option value="" disabled selected>-- Select your Church --</option>'
    if selected_district:
        for church in selected_district:
            options += f'<option value="{church.id}">AIC {church.name} Local Church</option>'

    return options


@council_router.get("/get-all-churches", response_class=HTMLResponse)
async def get_all_churches(request: Request, session: AsyncSession = Depends(get_session)):
    # Find the specific district from your 'region' object
    # (Assuming 'region' is available or fetched from DB)
    params = dict(request.query_params)
    district_id = next((v for k, v in params.items()
                       if "district" in k), None)
    print(district_id)
    if not district_id:
        return None

    selected_churches = await council_services.get_churches_by_district(
        uuid.UUID(district_id), session)
    print(selected_churches)
    options = '<option value="" disabled selected>-- Select Church --</option>'
    if selected_churches:
        for church in selected_churches:
            options += f'<option value="{church.id}">AIC {church.name} Local Church</option>'

    return options


@council_router.get("")
async def get_council_structure(request: Request, session: AsyncSession = Depends(get_session)):
    region = await council_services.get_region_with_hierarchy(session)
    region_exists = region is not None

    return templates.TemplateResponse(
        "council.html",
        {
            "request": request,
            "region": region,
            "region_exists": region_exists,
        }
    )


@council_router.get("/structure")
async def get_council_structure(request: Request, session: AsyncSession = Depends(get_session)):
    region = await council_services.get_region_with_hierarchy(session)
    region_exists = region is not None

    return templates.TemplateResponse(
        "structure.html",
        {
            "request": request,
            "region": region,
        }
    )


@council_router.post("/region/create")
async def region_create(name: str = Form(...), session: AsyncSession = Depends(get_session)):
    await council_services.create_region(name, session)
    return RedirectResponse(url="/council", status_code=303)


@council_router.post("/districts/create")
async def district_create(
    name: str = Form(...),
    region_id: str = Form(...),
    session: AsyncSession = Depends(get_session)
):

    await council_services.create_district(name, uuid.UUID(region_id), session)
    return RedirectResponse(url="/council", status_code=303)


@council_router.post("/locals/create")
async def local_create(
    name: str = Form(...),
    district_id: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    await council_services.create_church(name, uuid.UUID(district_id), session)
    return RedirectResponse(url="/council", status_code=303)
