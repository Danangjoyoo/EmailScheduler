from flask import Blueprint, request, session

from .schema import CreateUserPydantic
# from .controller import show_email, create_scheduled_email
from ...database import connection as conn

router = Blueprint(
    name="user", 
    import_name=__name__,
    url_prefix="/user",
    template_folder="/routers/user",
    )

@router.get("")
async def get_user():
    pass
    # return await show_email()

@router.post("")
async def post_user():
    pass
    # return await create_scheduled_email(EmailPydantic(**request.json))