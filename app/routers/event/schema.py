from pydantic import BaseModel
from datetime import datetime
from ...dependencies.utils import BaseSchema

class EventPydantic(BaseSchema):
    id: int
    owner_id: int
    email_subject: str
    email_content: str
    timestamp: datetime
    done: bool