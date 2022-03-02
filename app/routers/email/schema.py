from pydantic import BaseModel
from datetime import datetime
from ...dependencies.utils import BaseSchema

class EmailPydantic(BaseSchema):
    name: str
    address: str

class ScheduledEmailPydantic(BaseSchema):
    event_id: int
    email_subject: str
    email_content: str
    timestamp: datetime