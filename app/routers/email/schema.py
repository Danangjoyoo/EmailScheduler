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

class EmailBodyPydantic(BaseSchema):
    subject: Optional[str] = ""
    content: str

class EmailPydantic(BaseSchema):
    sender_id: int
    email_body_id: int
    timestamp: datetime
    sent: bool = False

class EmailRecipient(BaseSchema):
    email_id: int
    recipient_address_id: int