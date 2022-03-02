from pydantic import BaseModel

class CreateUserPydantic(BaseModel):
    name: str
    email: str
    password: str