import uuid
from pydantic import BaseModel
from datetime import datetime


class EventSchema(BaseModel):
    event_name: str
    event_type: str
    date_from: datetime
    date_to: datetime
    venue_church_id: uuid.UUID
    venue_district_id: uuid.UUID
    venue_region_id: uuid.UUID
    actual_venue: str
    target_group: str
