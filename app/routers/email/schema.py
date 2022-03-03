from typing import Optional
from pydantic import validator, validate_email
from datetime import datetime
from ...dependencies.utils import BaseSchema

class EmailAddressPydantic(BaseSchema):
    address: str

    @validator("address")
    def email_must_valid(cls, v):
        validate_email(v)
        return v

class EmailPydantic(BaseSchema):
    sender_id: int
    event_id: int
    subject: Optional[str] = ""
    content: str
    timestamp: datetime

class EditEmailPydantic(BaseSchema):
    subject: Optional[str] = None
    content: Optional[str] = None
    timestamp: Optional[datetime] = None

class ScheduledEmailPydantic(BaseSchema):
    event_id: int
    subject: Optional[str] = ""
    content: str
    timestamp: datetime