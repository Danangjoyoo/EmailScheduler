from pydantic import validator, validate_email
from ...dependencies.utils import BaseSchema

class UserPydantic(BaseSchema):
    password: str

class CreateUserPydantic(UserPydantic):
    email: str

    @validator("email")
    def email_must_valid(cls, v):
        validate_email(v)
        return v