from pydantic import validator
from email_validator import validate_email, EmailNotValidError
from ...dependencies.utils import BaseSchema

class UserPydantic(BaseSchema):
    password: str

class CreateUserPydantic(UserPydantic):
    email: str

    @validator("email")
    def email_must_valid(cls, v, values):
        validate_email(v)
        return v