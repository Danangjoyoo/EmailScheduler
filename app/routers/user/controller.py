from sqlalchemy import select, update
import smtplib, ssl

from .schema import CreateUserPydantic
from ...database import models, connection as conn
from ...dependencies.utils import create_response, status, extract_and_count_object

async def read_user():
    return 