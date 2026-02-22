import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload

from app.db.models import Region, District, Church


class CouncilService:

    # Region
    async def region_exists(self, session: AsyncSession) -> bool:
        result = await session.exec(select(Region))
        return result.first() is not None

    async def create_region(self, name: str, session: AsyncSession) -> Region:
        region_name = name.title()
        region = Region(name=region_name)
        session.add(region)
        await session.commit()
        await session.refresh(region)
        return region

    async def get_region(self, session: AsyncSession):
        region = await session.exec(select(Region))
        return region.first()

    async def get_region_with_hierarchy(self, session: AsyncSession):
        statement = (
            select(Region)
            .options(
                selectinload(Region.districts).selectinload(District.churches)
            )
        )
        result = await session.exec(statement)
        return result.first()

    # District

    async def create_district(self, name: str, region_id: uuid.UUID, session: AsyncSession) -> District:
        district_name = name.title()
        district = District(name=district_name, region_id=region_id)
        session.add(district)
        await session.commit()
        await session.refresh(district)
        return district

    async def get_districts(self, session: AsyncSession):
        statement = select(District).options(selectinload(District.churches))
        result = await session.exec(statement)
        return result.all()

    # Church

    async def create_church(self, name: str, district_id: uuid.UUID, session: AsyncSession) -> Church:
        church_name = name.title()
        church = Church(name=church_name, district_id=district_id)
        session.add(church)
        await session.commit()
        await session.refresh(church)
        return church

    async def get_churches(self, session: AsyncSession):
        statement = select(Church).options(selectinload(Church.district))
        result = await session.exec(statement)
        return result.all()
