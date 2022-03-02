from flask import Blueprint, g, request

from .controller import (
    show_email,
    create_email, 
    update_email,
    remove_email,
    create_scheduled_email,
    emailCrud
)
from .schema import EmailPydantic, ScheduledEmailPydantic
from ...dependencies.utils import create_response, status, QueryPaginationParams
from ...dependencies.log import logger
from ...database import connection as conn

router = Blueprint(
    name="email", 
    import_name=__name__,
    url_prefix="/email",
    template_folder="/routers/email",
    )

@router.get("")
async def get_email():
    try:
        return await show_email(request, g.session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))
    

@router.post("")
async def post_email():
    try:
        return await create_email(request, g.session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))

@router.put("/<id>")
async def put_email(id: int):
    try:
        return await update_email(request, id, g.session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))

@router.delete("/<id>")
async def delete_email(id: int):
    try:
        return await remove_email(id, g.session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))


@router.get("/scheduled_email")
async def get_scheduled_email():
    pass


@router.post("/save_email")
async def post_scheduled_email():
    try:
        async with conn.session() as session:
            return await create_scheduled_email(request, session)
    except Exception as e:
        logger.error(e)
        return create_response(status=status.error(e))