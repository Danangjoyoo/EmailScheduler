from pydantic import BaseModel
from datetime import datetime
from ...dependencies.utils import BaseSchema

class EventPydantic(BaseSchema):
    owner_id: int
    name: str