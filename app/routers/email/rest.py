from flask import Blueprint, request, session

from .controller import show_email, create_scheduled_email
from .schema import EmailPydantic
from ...dependencies.utils import get_query_dict

router = Blueprint(
    name="email", 
    import_name=__name__,
    url_prefix="/email",
    template_folder="/routers/email",
    )

@router.get("")
async def get_email():
    print(session)
    return await show_email()
    

@router.post("/save_email")
async def post_email():
    return await create_scheduled_email(EmailPydantic(**request.json))