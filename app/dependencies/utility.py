from typing import Optional
from pydantic import BaseModel

class CommonQueryGetter(BaseModel):
    fields: Optional[str] = None
    page: int = None
    limit: int = None
    sortBy: str = None
    sortType: str = None