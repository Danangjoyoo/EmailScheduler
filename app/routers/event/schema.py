from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from ...dependencies.utils import BaseSchema

class EventPydantic(BaseSchema):
    owner_id: int
    name: str

class EditEventPydantic(BaseSchema):
    owner_id: Optional[int] = None
    name: Optional[str] = None

class EventParticipant(BaseSchema):
    event_id: int
    address_id: int