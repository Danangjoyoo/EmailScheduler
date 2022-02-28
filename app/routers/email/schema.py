from pydantic import BaseModel
from datetime import datetime

class EmailPydantic(BaseModel):
    email_subject: str
    email_content: str
    timestamp: datetime