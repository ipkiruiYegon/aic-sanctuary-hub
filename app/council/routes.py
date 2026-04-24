import uuid
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.database import get_session
from app.council.service import CouncilService
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# Import the templates object from core/templates.py
from app.core.templates import templates
council_router = APIRouter()
council_services = CouncilService()  # Instantiate the service


@council_router.get("/get-churches", response_class=HTMLResponse)
async def get_churches(request: Request, session: AsyncSession = Depends(get_session)):
    # Find the specific district from your 'region' object
    # (Assuming 'region' is available or fetched from DB)
    params = dict(request.query_params)
    district_id = next((v for k, v in params.items()
                       if "district" in k), None)
    if not district_id:
        return None

    selected_district = await council_services.get_churches_by_district(
        uuid.UUID(district_id), session)

    options = '<option value="" disabled selected>-- Select Church --</option>'
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
